"""Extract Olympia School District rows from OSPI S-275 statewide personnel files.
Usage: python extract_s275.py <out_dir> <file.xlsx> [<file.xlsx> ...]
Writes <out_dir>/s275_olympia_rows.csv (person-level, LOCAL ONLY: contains names; do not publish).
School year is read from the file name. Olympia is matched on the 'School District' column == 'Olympia'.
"""
import sys, re, csv, openpyxl
cols = ['School District','Location Code','Building Location Name','Last Name','First Name','cert','Duty Title',
        'Cert FTE','Clas FTE','Cert Base Salary','Clas Base Salary','Total Salary','Insurance Benefits','Mandatory Benefits']
def run(out_dir, files):
    rows = []
    for f in files:
        sy = re.search(r'(\d{4})-(\d{4})', f).group(0)
        sy = sy[:4] + '-' + sy[7:]
        wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
        for ws in wb:
            it = ws.iter_rows(values_only=True)
            hdr = [h if h not in (None, ',') else f'_{i}' for i, h in enumerate(next(it))]
            ix = {c: hdr.index(c) for c in cols if c in hdr}
            found = False
            for r in it:
                dn = r[ix['School District']]
                if dn is None: continue
                if str(dn).strip().lower() == 'olympia':
                    found = True
                    rows.append([sy] + [r[ix[c]] if c in ix else None for c in cols[1:]])
            print(sy, ws.title, 'olympia rows so far', len(rows), flush=True)
    with open(f'{out_dir}/s275_olympia_rows.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(['school_year'] + [c.lower().replace(' ', '_') for c in cols[1:]]); w.writerows(rows)
if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2:])
