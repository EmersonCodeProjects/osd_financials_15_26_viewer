"""Assemble viewer/index.html from the clean tables and the decisions log.
Usage: python build_viewer.py --clean <clean_data_OSD> --decisions <DECISIONS_AND_INFERENCES.md> --template <viewer_template.html> --out <index.html>
No calculations happen here except moving values into a JSON object; calculations in the page are labeled CALCULATED and logged (V1, B1, E1)."""
import argparse, json, re
import pandas as pd

ap = argparse.ArgumentParser()
for a in ['clean', 'decisions', 'template', 'out']: ap.add_argument('--' + a, required=True)
a = ap.parse_args()
C = a.clean
st = pd.read_csv(f'{C}/staffing.csv'); en = pd.read_csv(f'{C}/enrollment.csv'); ex = pd.read_csv(f'{C}/f196_expenditures.csv')
rv = pd.read_csv(f'{C}/f196_revenues.csv'); ca = pd.read_csv(f'{C}/central_admin_measures.csv'); df = pd.read_csv(f'{C}/deflator.csv')
ys = sorted(st.school_year.unique()); yf = [y for y in sorted(ex.school_year.unique()) if y >= '2015-16']
order = ['district_administration', 'classified_director_supervisor', 'building_administration', 'teachers', 'other_certificated', 'paraeducators', 'classified_support', 'on_leave']
D = {'years_s275': ys, 'years_f196': yf, 'category_order': order}
D['labels'] = {'district_administration': 'District administration (11x-13x)', 'classified_director_supervisor': 'Classified directors/supervisors (99y)', 'building_administration': 'Building administration', 'teachers': 'Teachers', 'other_certificated': 'Other certificated', 'paraeducators': 'Paraeducators (aides)', 'classified_support': 'Classified support', 'on_leave': 'On paid leave', 'all_staff': 'All staff',
  'basic_education': 'Basic education', 'covid_relief_and_stabilization': 'COVID relief and stabilization', 'special_education': 'Special education', 'career_technical': 'Career and technical', 'learning_assistance_and_title': 'Learning assistance and Title', 'english_learners_bilingual': 'English learners / bilingual', 'highly_capable': 'Highly capable', 'other_instructional_programs': 'Other instructional programs', 'community_and_early_learning': 'Community and early learning', 'districtwide_support': 'Districtwide support', 'food_service': 'Food service', 'transportation': 'Transportation',
  'general_administration': 'General administration (activities 11-15)', 'building_administration_act': 'Building administration', 'teaching': 'Teaching', 'instructional_support_and_other_student_services': 'Instructional support and student services', 'maintenance_and_operations': 'Maintenance and operations', 'district_support_services': 'District support services', 'debt_service': 'Debt service', 'public_activities': 'Public activities',
  'certificated_salaries': 'Certificated salaries', 'classified_salaries': 'Classified salaries', 'benefits_and_payroll_taxes': 'Benefits and payroll taxes', 'supplies_and_materials': 'Supplies and materials', 'purchased_services': 'Purchased services', 'travel': 'Travel', 'capital_outlay': 'Capital outlay', 'transfers': 'Transfers (net about zero)', 'unlisted': 'Unlisted code',
  'local_taxes': 'Local taxes', 'local_non_tax': 'Local non-tax', 'state_general_purpose': 'State general purpose', 'state_special_purpose': 'State special purpose', 'federal_general_purpose': 'Federal general purpose', 'federal_special_purpose': 'Federal special purpose', 'other_school_districts': 'Other school districts', 'other_entities': 'Other entities', 'other_financing_sources': 'Other financing sources', 'of_which_covid_relief_federal': 'Of which federal COVID relief'}
cat = {}; title = {}
for (lv, c, m), g in st.groupby(['level', 'category', 'measure']):
    if m not in ('fte', 'headcount'): continue
    d = {r.school_year: float(r.value) for r in g.itertuples() if str(r.value) != 'nan'}
    if lv == 'category': cat.setdefault(c, {})[m] = d
    else: title.setdefault(c, {'category': None})[m] = d
tmap = pd.read_csv(f'{C}/s275_title_map.csv'); 
for t in title: title[t]['category'] = tmap.loc[tmap.duty_title == t, 'viewer_category'].iloc[0]
D['staffing'] = {'category': cat, 'title': title}
e = en[(en.measure == 'headcount_annual_avg')]
f_ = en[(en.measure == 'fte_annual_avg')]
D['enrollment'] = {'headcount_annual_avg': {r.school_year: float(r.value) for r in e.itertuples()}, 'fte_annual_avg': {r.school_year: float(r.value) for r in f_.itertuples()}}
D['deflator'] = {r.school_year: float(r.factor_to_ref_year_dollars) for r in df.itertuples()}
X = {}
for (gt, g), x in ex.groupby(['group_type', 'group']):
    if gt in ('program_group', 'activity_group', 'object_group'):
        key = 'building_administration_act' if (gt == 'activity_group' and g == 'building_administration') else g
        X.setdefault(gt, {})[key] = {r.school_year: float(r.dollars) for r in x.itertuples()}
X['total'] = {r.school_year: float(r.dollars) for r in ex[ex.group_type == 'total'].itertuples()}
D['expenditure'] = X
R = {}
for g, x in rv.groupby('group'): R[g] = {r.school_year: float(r.dollars) for r in x.itertuples()}
tot = {}
for g, x in R.items():
    if g.startswith('of_which'): continue
    for y, v in x.items(): tot[y] = tot.get(y, 0) + v
D['revenue'] = {'groups': R, 'total': tot}
Cn = {}
for r in ca.itertuples():
    if r.measure_id == 'district_stated' or str(r.dollars) in ('', 'nan'): continue
    pct = ''
    if r.measure_id == 'A': pct = str(r.note).replace(' of general fund', ' of GF')
    Cn.setdefault(r.measure_id, {})[r.school_year] = {'dollars': float(r.dollars), 'fte': None if str(r.fte) in ('', 'nan') else float(r.fte), 'people': None if str(r.people) in ('', 'nan') else int(float(r.people)), 'pct': pct}
D['central'] = Cn
D['flow_groups'] = ['front_office', 'classroom_teachers', 'paraeducators', 'student_services', 'support_staffing', 'super', 'managers', 'office_tech_prof', 'on_leave']

# --- conventional groupings (G1-G7), nested tiers (G6), community-list check (C4)
gr = pd.read_csv(f'{C}/staffing_grouped.csv'); G = {}; meta = {}
for r in gr.itertuples():
    meta[r.subgroup] = [r.side, r.group]
    if str(r.value) in ('', 'nan'): continue
    G.setdefault(r.view, {}).setdefault(r.subgroup, {}).setdefault(r.measure, {})[r.school_year] = float(r.value)
D['grouped'] = G; D['group_meta'] = meta
tr = pd.read_csv(f'{C}/district_tiers.csv'); T = {}
for r in tr.itertuples():
    T.setdefault(r.tier, {'label': r.label, 'fte': {}, 'people': {}, 'comp': {}})
    T[r.tier]['fte'][r.school_year] = float(r.fte); T[r.tier]['people'][r.school_year] = int(r.people)
    if str(r.comp_total) not in ('', 'nan'): T[r.tier]['comp'][r.school_year] = float(r.comp_total)
D['tiers'] = T
cm = pd.read_csv(f'{C}/community_match.csv'); dl = pd.read_csv(f'{C}/district_location_titles.csv'); D['district_location_titles'] = [{'year': r.school_year, 'title': r.duty_title, 'group': r.flow_group, 'fte': float(r.fte), 'people': str(r.people)} for r in dl.itertuples()]
rc = pd.read_csv(f'{C}/community_recon.csv'); D['community_recon'] = [{'year': r.school_year, 'side': r.side, 'line': r.line, 'people': int(r.people), 'fte': None if str(r.fte) in ('', 'nan') else float(r.fte), 'comp': None if str(r.comp) in ('', 'nan') else float(r.comp)} for r in rc.itertuples()]
dfl = pd.read_csv(f'{C}/district_location_flow.csv'); D['district_location_flow'] = [{'to': r.to_year, 'status': r.status, 'people': str(r.people), 'fte': None if str(r.fte_in_2022_23) in ('', 'nan') else float(r.fte_in_2022_23)} for r in dfl.itertuples()]
D['community_match'] = cm.drop(columns=['derivation', 'decision_ids']).to_dict('records')
cc = pd.read_csv(f'{C}/community_list_composition.csv'); D['community_composition'] = [{'year': r.school_year, 'group': r.flow_group, 'rows': int(r.rows), 'comp': None if str(r.compensation) in ('', 'nan') else float(r.compensation)} for r in cc.itertuples()]
tm = tmap.copy(); D['titles'] = [{'title': r.duty_title, 'category': r.viewer_category, 'group': r.flow_group, 'note': '' if str(r.note) == 'nan' else r.note} for r in tm.itertuples()]
D['labels'].update({'front_office': 'Front office (principals, vice principals, school administrators)', 'classroom_teachers': 'Classroom teachers (homeroom, specialist, secondary, other, substitute)', 'student_services': 'Student services (counselors, nurses, therapists, librarians, other support personnel)', 'support_staffing': 'Support staffing (bus, custodial, food service, trades, laborers)', 'super': 'Superintendent and deputy/assistant', 'managers': 'Managers (other district administrators, directors, supervisors)', 'office_tech_prof': 'Office, technical, professional (school or district)', 'district_staff': 'District office staff (2022-23 on)', 'district_office_staff': 'District office staff: office, technical, professional (coded to the district location)', 'district_other_coded': 'Other staff coded to the district location (trades, laborers, custodial/food service, aides, other support personnel)', 'school_clerical': 'School office staff (2022-23 on)', 'school_tech_prof': 'School technical/professional (2022-23 on)', 'student_facing': 'Student facing', 'district': 'District', 'unplaced': 'Cannot place before 2022-23'})

# --- pay (PY1-PY4, E4, X1)
def nz(x): return None if str(x) in ('', 'nan', '<5') else float(x)
pbg = pd.read_csv(f'{C}/pay_by_group.csv'); pc = pd.read_csv(f'{C}/pay_continuing.csv'); pp_ = pd.read_csv(f'{C}/pay_peers.csv'); ph = pd.read_csv(f'{C}/pay_high_earners.csv'); pe = pd.read_csv(f'{C}/pay_external_benchmarks.csv'); ps = pd.read_csv(f'{C}/pay_superintendent_position.csv'); bm = pd.read_csv(f'{C}/benchmarks.csv')
PAY = {'base': {}, 'total': {}, 'fte': {}, 'people': {}, 'cont': {}, 'peer': {}, 'high': {}, 'ext': {}, 'super': {}, 'cpi': {}, 'gwa': {}, 'gwr': {}, 'step': {}}
for r in pbg.itertuples():
    PAY['base'].setdefault(r.group, {})[r.school_year] = nz(r.base_per_fte); PAY['total'].setdefault(r.group, {})[r.school_year] = nz(r.salary_per_fte); PAY['fte'].setdefault(r.group, {})[r.school_year] = float(r.fte); PAY['people'].setdefault(r.group, {})[r.school_year] = int(r.people)
for r in pc.itertuples(): PAY['cont'].setdefault(r.group, {})[r.school_year] = nz(r.median_change)
for r in pp_.itertuples(): PAY['peer'].setdefault(r.group, {})[r.school_year] = {'olympia': nz(r.olympia_base_per_fte), 'state_n': int(r.state_districts), 'state_p25': nz(r.state_p25), 'state_median': nz(r.state_median), 'state_p75': nz(r.state_p75), 'pct': nz(r.olympia_percentile), 'sim_n': int(r.similar_size_districts), 'sim_median': nz(r.similar_median), 'sim_p75': nz(r.similar_p75), 'sim_pct': nz(r.olympia_percentile_similar)}
for r in ph.itertuples(): PAY['high'].setdefault(str(r.threshold), {})[r.school_year] = None if str(r.people) == '<5' else int(r.people); 
for r in ph.itertuples():
    if str(r.people) == '<5': PAY['high'][str(r.threshold)][r.school_year] = '<5'
for r in pe.itertuples(): PAY['ext'].setdefault(r.series, {})[r.school_year] = float(r.value)
for r in ps.itertuples(): PAY['super'][r.school_year] = {'base': float(r.base_salary), 'total': float(r.total_salary), 'insurance': float(r.insurance), 'mandatory': float(r.mandatory), 'fte': float(r.fte)}
for r in bm[(bm.series == 'seattle_cpi') & (bm.measure == 'index_1982_84=1')].itertuples(): PAY['cpi'][r.school_year] = float(r.value)
for r in bm[bm.series == 'state_employee_nonrep_general_increase'].itertuples(): PAY['gwa'][r.school_year] = float(r.value)
for r in bm[bm.series == 'state_employee_wfse_gg_general_increase'].itertuples(): PAY['gwr'][r.school_year] = float(r.value)
PAY['r65'] = {'top': {r.school_year: float(r.value) for r in bm[bm.series == 'wfse_gs_range65_top_step'].itertuples()}, 'a': {r.school_year: float(r.value) for r in bm[bm.series == 'wfse_gs_range65_step_a'].itertuples()}}
PAY['step'] = {'two_step': float(bm[(bm.series == 'wfse_gg_step_two_step_average') & (bm.school_year == '2023-24')].value.iloc[0]), 'a_to_l': float(bm[(bm.series == 'wfse_gg_step_spread_A_to_L') & (bm.school_year == '2023-24')].value.iloc[0]), 'a_to_m': float(bm[(bm.series == 'wfse_gg_step_spread_A_to_M') & (bm.school_year == '2023-24')].value.iloc[0])}
D['pay'] = PAY
D['labels'].update({'district_admin': 'Superintendent, deputy and district managers combined', 'office_clerical_school': 'Office and clerical: at schools', 'office_clerical_district': 'Office and clerical: district office', 'technical_professional_school': 'Technical and professional: at schools', 'technical_professional_district': 'Technical and professional: district office'})
D['labels'].update({'principals_vps': 'Principals and vice principals', 'bus_drivers': 'Bus drivers (operators)', 'custodial_food_service': 'Custodial and food service workers', 'trades_laborers': 'Trades and laborers', 'office_clerical': 'Office and clerical staff', 'technical_professional': 'Technical and professional staff', 'district_managers': 'District managers (other district administrators, directors, supervisors)', 'superintendent': 'Superintendent'})
# entries from the decisions log
E = {}
for line in open(a.decisions, encoding='utf-8'):
    m = re.match(r'^\|\s*([A-Z]\d+)\s*\|(.*)\|\s*$', line)
    if not m: continue
    cells = [re.sub(r'\*\*|`', '', c.strip()) for c in m.group(2).split('|')]
    if len(cells) < 4: continue
    E[m.group(1)] = {'what': cells[0], 'why': cells[1], 'effect': cells[2], 'status': cells[3] if len(cells) > 3 else ''}
html = open(a.template, encoding='utf-8').read().replace('/*DATA*/', json.dumps(D, separators=(',', ':'))).replace('/*ENTRIES*/', json.dumps(E, separators=(',', ':')))
open(a.out, 'w', encoding='utf-8').write(html)
print('entries', len(E), 'bytes', len(html))
