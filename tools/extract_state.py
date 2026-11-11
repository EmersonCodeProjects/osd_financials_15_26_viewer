import sys, re, csv, openpyxl, glob
# statewide S-275, NO names kept. Output: one csv for all districts.
cols=['School District','Location Code','Duty Title','Cert FTE','Clas FTE','Cert Base Salary','Clas Base Salary','Total Salary','Insurance Benefits','Mandatory Benefits']
out=open('/home/claude/work/state/s275_state_noname.csv','w',newline='',encoding='utf-8'); w=csv.writer(out); w.writerow(['school_year']+[c.lower().replace(' ','_') for c in cols])
for f in sorted(glob.glob('/mnt/user-data/uploads/2026_OSD_Closure/phase2_data_explorer/raw_data_OSD/s-275/washington_state_school_personnel_*.xlsx')):
    sy=re.search(r'(\d{4})-(\d{4})',f).group(0); sy=sy[:4]+'-'+sy[7:]
    wb=openpyxl.load_workbook(f,read_only=True,data_only=True); n=0
    for ws in wb:
        it=ws.iter_rows(values_only=True); hdr=[h if h not in (None,',') else f'_{i}' for i,h in enumerate(next(it))]
        ix={c:hdr.index(c) for c in cols if c in hdr}
        for r in it:
            if r[ix['School District']] is None: continue
            w.writerow([sy]+[r[ix[c]] if c in ix else None for c in cols]); n+=1
    print(sy,n,flush=True)
out.close()
