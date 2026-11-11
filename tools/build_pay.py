"""Pay tables (Phase 2, Stage 1: compensation).  Usage:
  python build_pay.py --olympia <s275_olympia_rows.csv (LOCAL, has names)> --state <s275_state_noname.csv> --maps <clean dir> --out <clean dir>
Writes aggregate tables only (no names).  Base pay per FTE = sum(base salary) / sum(FTE) (base excludes extra pay, which varies year to year); total salary per FTE is also kept for rows with FTE > 0.  Counts under 5 people are suppressed (P4),
except the superintendent position, which is published by title only (decision E4)."""
import argparse, re, numpy as np, pandas as pd
ap = argparse.ArgumentParser(); ap.add_argument('--olympia'); ap.add_argument('--state'); ap.add_argument('--maps'); ap.add_argument('--out'); a = ap.parse_args()
MIN_N = 5
tm = pd.read_csv(f'{a.maps}/s275_title_map.csv'); fg = dict(zip(tm.duty_title, tm.flow_group))
def prep(d):
    d = d.copy(); d['fte'] = d.cert_fte.fillna(0) + d.clas_fte.fillna(0)
    for c in ['total_salary', 'insurance_benefits', 'mandatory_benefits']: d[c] = pd.to_numeric(d[c], errors='coerce').fillna(0)
    d['base'] = pd.to_numeric(d.cert_base_salary, errors='coerce').fillna(0) + pd.to_numeric(d.clas_base_salary, errors='coerce').fillna(0)
    d['comp'] = d.total_salary + d.insurance_benefits + d.mandatory_benefits
    d['group'] = d.duty_title.map(fg); return d[d.fte > 0]
O = prep(pd.read_csv(a.olympia)); S = prep(pd.read_csv(a.state)); S['district'] = S.school_district.astype(str).str.strip()
O['person'] = O.last_name.str.upper().str.strip() + '|' + O.first_name.str.upper().str.strip()
# pay groups used on the page (job-title basis, all years)
PG = {'principals_vps': ['Elementary Principal', 'Secondary Principal', 'Elem. Vice Principal', 'Secondary Vice Principal'], 'classroom_teachers': ['Elem. Homeroom Teacher', 'Elem. Specialist Teacher', 'Secondary Teacher', 'Other Teacher'],
      'paraeducators': ['Aide'], 'student_services': ['Counselor', 'Library Media Specialist', 'Nurse', 'Psychologist', 'Social Worker', 'Occupational Therapist', 'Physical Therapist', 'Spch.-Lang. Path./Audio.'],
      'bus_drivers': ['Operator'], 'custodial_food_service': ['Service Worker'], 'trades_laborers': ['Crafts/Trades', 'Laborer'], 'office_clerical': ['Office/Clerical'], 'technical_professional': ['Technical', 'Professional'],
      'district_managers': ['Other District Admin.', 'Director/Supervisor'], 'superintendent': ['Superintendent'],
      # PY5: the non-student-facing administrative line (same titles as the 'super' + 'managers' groups on the Charts tab)
      'district_admin': ['Superintendent', 'Deputy/Assist. Supt.', 'Other District Admin.', 'Director/Supervisor'],
      # PY6: office, clerical, technical and professional staff split by where S-275 codes them (building column exists from 2022-23 only; district office = location 1035)
      'office_clerical_school': (['Office/Clerical'], 'school'), 'office_clerical_district': (['Office/Clerical'], 'district'),
      'technical_professional_school': (['Technical', 'Professional'], 'school'), 'technical_professional_district': (['Technical', 'Professional'], 'district')}
SPLIT = {g for g, v in PG.items() if isinstance(v, tuple)}
def grp_rows(df, spec):
    titles, loc = spec if isinstance(spec, tuple) else (spec, None)
    x = df[df.duty_title.isin(titles)]
    if loc and 'location_code' in x:
        lc = pd.to_numeric(x.location_code, errors='coerce')
        x = x[(lc == 1035)] if loc == 'district' else x[lc.notna() & (lc != 1035)]
    return x
# 1. Olympia pay per FTE by group
rec = []
for sy in sorted(O.school_year.unique()):
    for g, ts in PG.items():
        x = grp_rows(O[O.school_year == sy], ts); n = x.person.nunique()
        if len(x) == 0: continue
        sup = n < MIN_N and g != 'superintendent'
        rec.append(dict(school_year=sy, group=g, fte=round(x.fte.sum(), 2), people=n, base_per_fte='' if sup else round(x.base.sum() / x.fte.sum()), salary_per_fte='' if sup else round(x.total_salary.sum() / x.fte.sum()), comp_per_fte='' if sup else round(x.comp.sum() / x.fte.sum()), suppressed='Y' if sup else '', derivation='CALCULATED', decision_ids='PY1,P4,S3' + (',E4' if g == 'superintendent' else '')))
pd.DataFrame(rec).to_csv(f'{a.out}/pay_by_group.csv', index=False)
# 2. same-people pay change: continuing people, same group both years, median % change in salary per FTE
O = O.sort_values(['school_year']); cont = []
yrs = sorted(O.school_year.unique())
for g, ts in PG.items():
    if g == 'superintendent': continue
    for y0, y1 in zip(yrs[:-1], yrs[1:]):
        def pp(y):
            x = grp_rows(O[O.school_year == y], ts); t = x.groupby('person').agg(f=('fte', 'sum'), s=('base', 'sum')); t = t[t.f >= 0.5]; t['p'] = t.s / t.f; return t.p
        p0, p1 = pp(y0), pp(y1); both = p0.index.intersection(p1.index); ch = (p1[both] / p0[both] - 1)
        ch = ch[(ch > -0.5) & (ch < 1.0)]; n = len(ch)
        cont.append(dict(school_year=y1, group=g, continuing_people=n if n >= MIN_N else '<5', median_change='' if n < MIN_N else round(float(ch.median()), 4), mean_change='' if n < MIN_N else round(float(ch.mean()), 4), derivation='INFERRED', decision_ids='PY2,P1,S10,P4'))
pd.DataFrame(cont).to_csv(f'{a.out}/pay_continuing.csv', index=False)
# 3. peers: district-level average pay per FTE for each group, statewide and similar-size districts (size = total FTE)
size = S.groupby(['school_year', 'district']).fte.sum().rename('size').reset_index()
peer = []
for sy in sorted(S.school_year.unique()):
    sz = size[size.school_year == sy].set_index('district')['size']; osz = sz.get('Olympia', np.nan)
    similar = set(sz[(sz >= osz * 0.5) & (sz <= osz * 2)].index) - {'Olympia'}
    for g, ts in PG.items():
        if g in SPLIT: continue   # state file has no comparable district-office coding
        x = grp_rows(S[S.school_year == sy], ts)
        agg = x.groupby('district').agg(f=('fte', 'sum'), s=('base', 'sum'), n=('fte', 'size'))
        minn = 1 if g == 'superintendent' else 5
        agg = agg[(agg.n >= minn) & (agg.f > 0)]; agg['p'] = agg.s / agg.f
        if 'Olympia' not in agg.index: continue
        ov = agg.loc['Olympia', 'p']; allp = agg.p.drop('Olympia'); sim = agg.p[agg.index.isin(similar)]
        peer.append(dict(school_year=sy, group=g, olympia_base_per_fte='' if (g != 'superintendent' and agg.loc['Olympia', 'n'] < MIN_N) else round(ov),
                         state_districts=len(allp), state_p25=round(allp.quantile(.25)), state_median=round(allp.median()), state_p75=round(allp.quantile(.75)), state_max='' if g == 'superintendent' else round(allp.max()),
                         olympia_percentile=round(float((allp < ov).mean() * 100), 1), similar_size_districts=len(sim), similar_median=round(sim.median()) if len(sim) else '', similar_p75=round(sim.quantile(.75)) if len(sim) else '',
                         olympia_percentile_similar=round(float((sim < ov).mean() * 100), 1) if len(sim) else '', derivation='CALCULATED', decision_ids='PY3,P4' + (',E4' if g == 'superintendent' else '')))
pd.DataFrame(peer).to_csv(f'{a.out}/pay_peers.csv', index=False)
# 4. high earners (annualized salary per FTE >= thresholds), excluding the superintendent title; counts under 5 shown as '<5'
hi = []
for sy in yrs:
    x = O[(O.school_year == sy) & (O.duty_title != 'Superintendent')]
    t = x.groupby('person').agg(f=('fte', 'sum'), s=('base', 'sum'), tl=('duty_title', lambda s: s.iloc[0])); t = t[t.f >= 0.5]; t['p'] = t.s / t.f
    for th in (150000, 179700, 200000, 220644):
        n = int((t.p >= th).sum()); hi.append(dict(school_year=sy, threshold=th, people='<5' if 0 < n < MIN_N else n, derivation='CALCULATED', decision_ids='PY4,P4'))
pd.DataFrame(hi).to_csv(f'{a.out}/pay_high_earners.csv', index=False)
# 5. superintendent position (published by title only; decision E4)
sp = O[O.duty_title == 'Superintendent'].groupby('school_year').agg(fte=('fte', 'sum'), base_salary=('cert_base_salary', 'sum'), total_salary=('total_salary', 'sum'), insurance=('insurance_benefits', 'sum'), mandatory=('mandatory_benefits', 'sum')).reset_index()
sp['derivation'] = 'RAW'; sp['decision_ids'] = 'E4,S3'; sp.to_csv(f'{a.out}/pay_superintendent_position.csv', index=False)
print('done', len(rec), len(cont), len(peer), len(hi))
