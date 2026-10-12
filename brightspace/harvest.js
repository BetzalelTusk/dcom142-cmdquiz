/* CCBC Brightspace harvester (v2).
 *
 * HOW TO USE
 *   1. Log into https://ccbcmd.brightspace.com and open any page.
 *   2. F12 -> Console -> paste this whole file -> Enter.
 *   3. Run:  await harvest()             // metadata + assignment attachments
 *      or:   await harvest({files:true}) // the above + every course content file
 *   4. Keep the downloads private: course materials belong to your instructors and publishers.
 *
 * Read-only: only issues GETs against your own session. Courses are discovered from
 * your own enrollments, so nothing about any particular student is hard-coded here.
 * Bulk downloads need Brave/Chrome to allow automatic multiple downloads for this site.
 */
(() => {
  const X = localStorage.getItem('XSRF.Token');
  const LE = '1.97';
  const WINDOW_START = '2026-01-01T00:00:00.000Z';
  const WINDOW_END = '2027-06-30T23:59:59.000Z';

  const LP = '1.43';
  // Course offerings you are enrolled in, as [short code, org unit id].
  // Unpublished course shells answer 403 and are reported as unavailable.
  const myCourses = async () => {
    const r = await fetch(`/d2l/api/lp/${LP}/enrollments/myenrollments/?pageSize=100`, { credentials: 'same-origin' });
    const v = r.ok ? await r.json() : {};
    return (v.Items || [])
      .filter((e) => e.OrgUnit && e.OrgUnit.Type && e.OrgUnit.Type.Code === 'Course Offering')
      .map((e) => [(e.OrgUnit.Name.match(/\b([A-Z]{3,4}\d{3})\b/) || [])[1] || e.OrgUnit.Name, e.OrgUnit.Id]);
  };

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const soft = async (p) => {
    try {
      const r = await fetch(p, { credentials: 'same-origin', headers: { 'X-Csrf-Token': X } });
      return r.ok ? await r.json() : null;
    } catch (e) { return null; }
  };
  // Endpoints disagree on shape: some return a bare array, others {Objects:[...]}.
  const arr = (v) => (Array.isArray(v) ? v : (v && Array.isArray(v.Objects) ? v.Objects : []));
  const save = (blob, name) => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
  };
  const clean = (s) => (s || '').replace(/[<>:"|?*\\/]/g, '_');

  // content/toc returns the whole tree in one request. content/root/ does NOT -
  // it returns a shallow skeleton and silently drops deep sub-modules.
  const walk = (mods, path, acc) => {
    for (const m of mods || []) {
      acc.modules.push({
        id: m.ModuleId, title: m.Title, path: path.join(' / '),
        start: m.StartDateTime, end: m.EndDateTime, hidden: m.IsHidden,
      });
      for (const t of m.Topics || []) {
        acc.topics.push({
          id: t.TopicId, title: t.Title, path: path.concat(m.Title).join(' / '),
          type: t.TypeIdentifier, url: t.Url || null, due: t.DueDate || null,
          start: t.StartDateTime, end: t.EndDateTime, hidden: t.IsHidden,
        });
      }
      walk(m.Modules, path.concat(m.Title), acc);
    }
    return acc;
  };

  window.harvest = async (opts = {}) => {
    const out = { generated: new Date().toISOString(), courses: {}, unavailable: [] };

    for (const [key, ou] of await myCourses()) {
      const toc = await soft(`/d2l/api/le/${LE}/${ou}/content/toc`);
      if (!toc) {
        out.unavailable.push({ course: key, orgUnit: ou, reason: '403 - course shell not published yet' });
        continue;
      }
      const acc = walk(toc.Modules, [], { modules: [], topics: [] });

      const dz = arr(await soft(`/d2l/api/le/${LE}/${ou}/dropbox/folders/`));
      const gi = arr(await soft(`/d2l/api/le/${LE}/${ou}/grades/`));
      const gv = arr(await soft(`/d2l/api/le/${LE}/${ou}/grades/values/myGradeValues/`));
      const nw = arr(await soft(`/d2l/api/le/${LE}/${ou}/news/`));
      const qz = arr(await soft(`/d2l/api/le/${LE}/${ou}/quizzes/`));
      const sv = arr(await soft(`/d2l/api/le/${LE}/${ou}/surveys/`));
      const cal = arr(await soft(`/d2l/api/le/${LE}/${ou}/calendar/events/myEvents/` +
        `?startDateTime=${WINDOW_START}&endDateTime=${WINDOW_END}`));

      const discussions = [];
      for (const f of arr(await soft(`/d2l/api/le/${LE}/${ou}/discussions/forums/`))) {
        const topics = [];
        for (const t of arr(await soft(`/d2l/api/le/${LE}/${ou}/discussions/forums/${f.ForumId}/topics/`))) {
          const posts = arr(await soft(
            `/d2l/api/le/${LE}/${ou}/discussions/forums/${f.ForumId}/topics/${t.TopicId}/posts/`));
          topics.push({
            id: t.TopicId, name: t.Name, description: (t.Description && t.Description.Text) || '',
            start: t.Availability && t.Availability.StartDate,
            end: t.Availability && t.Availability.EndDate,
            // Message.Text is empty on discussion posts - the content is in Message.Html.
            posts: posts.map((p) => ({
              id: p.PostId, subject: p.Subject,
              body: (p.Message && (p.Message.Text || p.Message.Html)) || '',
              date: p.DatePosted, by: p.PostingUserDisplayName || p.PostingUserId,
            })),
          });
        }
        discussions.push({ id: f.ForumId, name: f.Name, description: (f.Description && f.Description.Text) || '', topics });
      }

      // Checklist items hang off the CHECKLIST, not the category, and come back
      // as {Objects:[...]}. Querying categories/{id}/items/ returns nothing.
      const checklists = [];
      for (const c of arr(await soft(`/d2l/api/le/${LE}/${ou}/checklists/`))) {
        const items = arr(await soft(`/d2l/api/le/${LE}/${ou}/checklists/${c.ChecklistId}/items/`));
        checklists.push({
          id: c.ChecklistId, name: c.Name,
          items: items.map((i) => ({ id: i.ChecklistItemId, name: i.Name, due: i.DueDate })),
        });
      }

      // Assignment attachments are NOT content topics - harvesting only the
      // content tree misses them entirely.
      const attachments = [];
      for (const f of dz) {
        for (const a of f.Attachments || []) {
          attachments.push({
            folderId: f.Id, folder: f.Name, fileId: a.FileId, name: a.FileName, size: a.Size,
            url: `/d2l/api/le/${LE}/${ou}/dropbox/folders/${f.Id}/attachments/${a.FileId}`,
          });
        }
      }

      out.courses[key] = {
        orgUnit: ou,
        modules: acc.modules,
        topics: acc.topics,
        assignments: dz.map((f) => ({
          id: f.Id, name: f.Name, due: f.DueDate,
          start: f.Availability && f.Availability.StartDate,
          end: f.Availability && f.Availability.EndDate,
          points: f.Assessment && f.Assessment.ScoreDenominator,
          instructions: (f.CustomInstructions && f.CustomInstructions.Text) || '',
          attachments: (f.Attachments || []).map((a) => a.FileName),
        })),
        gradeItems: gi.map((g) => ({ id: g.Id, name: g.Name, max: g.MaxPoints, weight: g.Weight, type: g.GradeType })),
        myGrades: gv.map((v) => ({
          id: v.GradeObjectIdentifier, name: v.GradeObjectName,
          points: v.PointsNumerator, of: v.PointsDenominator, display: v.DisplayedGrade,
        })),
        news: nw.map((n) => ({ id: n.Id, title: n.Title, start: n.StartDate, body: (n.Body && n.Body.Text) || '' })),
        quizzes: qz.map((q) => ({ id: q.QuizId, name: q.Name, due: q.DueDate, start: q.StartDate, end: q.EndDate })),
        // All-day events leave StartDateTime null and carry StartDay/EndDay instead.
        calendar: cal.map((e) => ({
          id: e.CalendarEventId, title: e.Title,
          start: e.StartDateTime || e.StartDay || null,
          end: e.EndDateTime || e.EndDay || null,
          allDay: e.IsAllDayEvent,
        })),
        surveys: sv.map((s) => ({ id: s.SurveyId, name: s.Name })),
        discussions, checklists, attachments,
      };
    }

    save(new Blob([JSON.stringify(out, null, 2)], { type: 'application/json' }), 'CCBC__ccbc-full.json');
    await sleep(600);

    const report = { unavailable: out.unavailable, attachments: 0, contentFiles: 0, failed: [] };

    for (const key of Object.keys(out.courses)) {
      for (const a of out.courses[key].attachments) {
        try {
          const r = await fetch(a.url, { credentials: 'same-origin', headers: { 'X-Csrf-Token': X } });
          if (!r.ok) { report.failed.push({ name: a.name, status: r.status }); continue; }
          save(await r.blob(), 'CCBC__' + key + '__' + clean(a.name));
          report.attachments++;
          await sleep(500);
        } catch (e) { report.failed.push({ name: a.name, err: String(e.message) }); }
      }
    }

    if (opts.files) {
      for (const key of Object.keys(out.courses)) {
        for (const t of out.courses[key].topics) {
          if (t.type !== 'File' || !t.url) continue;
          try {
            const r = await fetch(t.url, { credentials: 'same-origin', headers: { 'X-Csrf-Token': X } });
            if (!r.ok) { report.failed.push({ name: t.title, status: r.status }); continue; }
            save(await r.blob(), 'CCBC__' + key + '__' + clean(decodeURIComponent(t.url.split('/').pop())));
            report.contentFiles++;
            await sleep(500);
          } catch (e) { report.failed.push({ name: t.title, err: String(e.message) }); }
        }
      }
    }

    for (const k of Object.keys(out.courses)) {
      const c = out.courses[k];
      report[k] = {
        modules: c.modules.length, topics: c.topics.length,
        assignments: c.assignments.length, forums: c.discussions.length,
        checklistItems: c.checklists.reduce((n, x) => n + x.items.length, 0),
        dated: c.calendar.filter((e) => e.start).length,
      };
    }

    window.__harvest = out;
    console.log(report);
    return report;
  };

  console.log('harvest() ready. Run:  await harvest()   or   await harvest({files:true})');
})();
