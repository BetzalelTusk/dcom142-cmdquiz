/* Brightspace API probe — run in the browser console while logged in.
   Read-only. Uses your existing session; touches nothing but GETs. */
(async () => {
  const out = { origin: location.origin, xsrf: null, versions: null, enrollments: null, errors: [] };

  // Brightspace stashes a CSRF token; GETs usually don't need it, but send it if we find one.
  try {
    out.xsrf = localStorage.getItem('XSRF.Token')
      || (window.D2L?.LP?.Web?.Authentication?.Xsrf?.GetXsrfToken?.());
  } catch (e) { out.errors.push('xsrf: ' + e.message); }

  const get = async (path) => {
    const h = out.xsrf ? { 'X-Csrf-Token': out.xsrf } : {};
    const r = await fetch(path, { credentials: 'same-origin', headers: h });
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    return r.json();
  };

  // 1. Is the Valence API exposed at all, and at which versions?
  try {
    const v = await get('/d2l/api/versions/');
    out.versions = Object.fromEntries(v.map(p => [p.ProductCode, p.LatestVersion]));
  } catch (e) { out.errors.push('versions: ' + e.message); }

  // 2. Can we list our own enrollments?
  const lp = out.versions?.lp || '1.9';
  try {
    const e = await get(`/d2l/api/lp/${lp}/enrollments/myenrollments/?orgUnitTypeId=3`);
    out.enrollments = (e.Items || []).map(i => ({
      id: i.OrgUnit?.Id, name: i.OrgUnit?.Name, code: i.OrgUnit?.Code
    }));
  } catch (e) { out.errors.push('enrollments: ' + e.message); }

  console.log(JSON.stringify(out, null, 2));
  return out;
})();
