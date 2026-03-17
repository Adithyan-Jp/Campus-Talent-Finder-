import streamlit as st
import mysql.connector
import pandas as pd
from datetime import date

st.set_page_config(page_title="Campus Talent Finder", layout="wide", page_icon="🎓")

# ─── RUN THESE SQL COMMANDS IN MYSQL FIRST ───────────────────────────────────
# ALTER TABLE Students ADD COLUMN IF NOT EXISTS Email VARCHAR(100) DEFAULT '';
# ALTER TABLE Skills   ADD COLUMN IF NOT EXISTS Category    VARCHAR(50)  DEFAULT 'Other';
# ALTER TABLE Skills   ADD COLUMN IF NOT EXISTS Difficulty  VARCHAR(20)  DEFAULT 'Medium';
# ALTER TABLE Skills   ADD COLUMN IF NOT EXISTS Description VARCHAR(255) DEFAULT '';
# CREATE TABLE IF NOT EXISTS Projects (
#   ProjectID INT AUTO_INCREMENT PRIMARY KEY, Title VARCHAR(200) NOT NULL,
#   Description TEXT, Status VARCHAR(50) DEFAULT 'Planning',
#   StartDate DATE, EndDate DATE);
# CREATE TABLE IF NOT EXISTS Project_Requirements (
#   ProjectID INT, SkillID INT, Importance VARCHAR(50) DEFAULT 'Required',
#   PRIMARY KEY (ProjectID,SkillID),
#   FOREIGN KEY (ProjectID) REFERENCES Projects(ProjectID),
#   FOREIGN KEY (SkillID) REFERENCES Skills(SkillID));
# CREATE TABLE IF NOT EXISTS Project_Members (
#   ProjectID INT, StudentID INT, Role VARCHAR(100), JoinedDate DATE,
#   PRIMARY KEY (ProjectID,StudentID),
#   FOREIGN KEY (ProjectID) REFERENCES Projects(ProjectID),
#   FOREIGN KEY (StudentID) REFERENCES Students(StudentID));
# CREATE TABLE IF NOT EXISTS Milestones (
#   MilestoneID INT AUTO_INCREMENT PRIMARY KEY, ProjectID INT NOT NULL,
#   Title VARCHAR(200), Deadline DATE, Status VARCHAR(50) DEFAULT 'Pending',
#   FOREIGN KEY (ProjectID) REFERENCES Projects(ProjectID));
# CREATE TABLE IF NOT EXISTS Task_Allocation (
#   TaskID INT AUTO_INCREMENT PRIMARY KEY, MilestoneID INT NOT NULL,
#   StudentID INT NOT NULL, TaskName VARCHAR(200), TaskStatus VARCHAR(50) DEFAULT 'To Do',
#   FOREIGN KEY (MilestoneID) REFERENCES Milestones(MilestoneID),
#   FOREIGN KEY (StudentID) REFERENCES Students(StudentID));
# CREATE TABLE IF NOT EXISTS Skill_Endorsements (
#   EndorsementID INT AUTO_INCREMENT PRIMARY KEY, StudentID INT NOT NULL,
#   SkillID INT NOT NULL, EndorserID INT NOT NULL, EndorsedDate DATE DEFAULT (CURRENT_DATE),
#   FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
#   FOREIGN KEY (SkillID) REFERENCES Skills(SkillID),
#   FOREIGN KEY (EndorserID) REFERENCES Students(StudentID));
# CREATE TABLE IF NOT EXISTS Project_Reviews (
#   ReviewID INT AUTO_INCREMENT PRIMARY KEY, ProjectID INT NOT NULL,
#   ReviewerName VARCHAR(200), Rating INT, Comments TEXT,
#   ReviewDate DATE DEFAULT (CURRENT_DATE),
#   FOREIGN KEY (ProjectID) REFERENCES Projects(ProjectID));

# ─── DB ───────────────────────────────────────────────────────────────────────
def get_db():
    return mysql.connector.connect(
        host="localhost", user="root", password="", database="campusprojectdb")

def q(sql, params=None):
    try:
        conn=get_db(); cur=conn.cursor(dictionary=True)
        cur.execute(sql, params or ()); rows=cur.fetchall()
        cur.close(); conn.close(); return rows
    except Exception as e:
        st.error(f"DB Error: {e}"); return []

def run(sql, params=None):
    try:
        conn=get_db(); cur=conn.cursor()
        cur.execute(sql, params or ()); lid=cur.lastrowid
        conn.commit(); cur.close(); conn.close(); return lid
    except Exception as e:
        st.error(f"DB Error: {e}"); return None

def fetch_students():
    return q("""SELECT s.StudentID as id,s.Name as name,s.Department as dept,s.Year as year,
                sk.SkillName as skill,ss.Proficiency as prof,COALESCE(s.Email,'') as email
                FROM Students s JOIN StudentSkills ss ON s.StudentID=ss.StudentID
                JOIN Skills sk ON ss.SkillID=sk.SkillID ORDER BY s.StudentID""")

def fetch_skills():
    return q("""SELECT SkillID as id,SkillName as name,COALESCE(Category,'Other') as cat,
                COALESCE(Difficulty,'Medium') as diff,COALESCE(Description,'') as descr
                FROM Skills ORDER BY SkillName""")

def fetch_projects():
    return q("""SELECT ProjectID as id,Title as title,COALESCE(Description,'') as descr,
                COALESCE(Status,'Planning') as status,StartDate as start_date,EndDate as end_date
                FROM Projects ORDER BY ProjectID DESC""")

def fetch_milestones():
    return q("""SELECT m.MilestoneID as id,m.ProjectID as project_id,p.Title as project_title,
                m.Title as title,m.Deadline as deadline,COALESCE(m.Status,'Pending') as status
                FROM Milestones m JOIN Projects p ON m.ProjectID=p.ProjectID ORDER BY m.Deadline""")

def fetch_tasks():
    return q("""SELECT t.TaskID as id,t.MilestoneID as milestone_id,mi.Title as milestone_title,
                p.Title as project_title,s.Name as student_name,t.TaskName as task_name,
                COALESCE(t.TaskStatus,'To Do') as status
                FROM Task_Allocation t JOIN Milestones mi ON t.MilestoneID=mi.MilestoneID
                JOIN Projects p ON mi.ProjectID=p.ProjectID
                JOIN Students s ON t.StudentID=s.StudentID ORDER BY t.TaskID DESC""")

def fetch_reviews():
    return q("""SELECT r.ReviewID as id,p.Title as project_title,r.ReviewerName as reviewer,
                r.Rating as rating,COALESCE(r.Comments,'') as comments,r.ReviewDate as review_date
                FROM Project_Reviews r JOIN Projects p ON r.ProjectID=p.ProjectID
                ORDER BY r.ReviewID DESC""")

def fetch_endorsements():
    return q("""SELECT e.EndorsementID as id,s.Name as student_name,sk.SkillName as skill_name,
                en.Name as endorser_name,e.EndorsedDate as edate
                FROM Skill_Endorsements e JOIN Students s ON e.StudentID=s.StudentID
                JOIN Skills sk ON e.SkillID=sk.SkillID JOIN Students en ON e.EndorserID=en.StudentID
                ORDER BY e.EndorsementID DESC""")

# ─── HTML UI ──────────────────────────────────────────────────────────────────
def build_html(students_data, skills_data, projects_data, tasks_data, reviews_data):
    DC={"CS":"#6c63ff","AI/ML":"#4ecdc4","IT":"#ffd93d","EC":"#ff6b6b","Mechanical":"#6bcb77"}
    SC={"Planning":"#ffd93d","Active":"#6bcb77","Completed":"#4ecdc4","On Hold":"#ff6b6b"}
    TC={"To Do":"#8b91a8","In Progress":"#ffd93d","Done":"#6bcb77","Blocked":"#ff6b6b"}
    CC={"Programming":"#6c63ff","Framework":"#4ecdc4","Database":"#ffd93d","Design":"#ff6b6b","Hardware":"#6bcb77","Other":"#a78bfa"}
    YM={1:"1st",2:"2nd",3:"3rd",4:"4th"}
    def dc(d): return DC.get(d,"#888")
    def cc(c): return CC.get(c,"#888")
    def ini(n): return "".join(w[0] for w in (n or "").split() if w)[:2].upper() or "??"
    def skct(name): return sum(1 for s in students_data if s.get("skill")==name)

    total_students=len(students_data); total_skills=len(skills_data)
    total_projects=len(projects_data); active_proj=sum(1 for p in projects_data if p.get("status")=="Active")
    adv=sum(1 for s in students_data if s.get("prof")=="Advanced")
    done_tasks=sum(1 for t in tasks_data if t.get("status")=="Done")
    total_tasks=len(tasks_data); task_pct=int(done_tasks/total_tasks*100) if total_tasks else 0

    import json
    js_stu=json.dumps([{"id":s["id"],"name":s["name"],"dept":s["dept"],"year":s["year"],"skill":s["skill"],"prof":s["prof"],"email":s.get("email","")} for s in students_data])
    js_sk=json.dumps([{"id":sk["id"],"name":sk["name"],"cat":sk.get("cat","Other"),"diff":sk.get("diff","")} for sk in skills_data])
    js_tasks=json.dumps([{"task_name":t["task_name"],"project_title":t["project_title"],"milestone_title":t["milestone_title"],"student_name":t["student_name"],"status":t["status"]} for t in tasks_data])

    depts={}
    for s in students_data: depts[s["dept"]]=depts.get(s["dept"],0)+1
    mx=max(depts.values(),default=1)
    dept_html="".join(f'<div class="db-row"><div class="db-lbl">{d}</div><div class="db-track"><div class="db-inner" style="width:{c/mx*100:.0f}%;background:{dc(d)};color:#0a0c10">{c}</div></div><div class="db-ct">{c}</div></div>' for d,c in sorted(depts.items(),key=lambda x:-x[1]))

    sc={}
    for s in students_data: sc[s["skill"]]=sc.get(s["skill"],0)+1
    cols=["#6c63ff","#4ecdc4","#ffd93d","#ff6b6b","#6bcb77","#a78bfa"]
    top6=sorted(sc.items(),key=lambda x:-x[1])[:6]
    top_html='<div style="display:grid;grid-template-columns:1fr 1fr;gap:9px">'+"".join(f'<div style="background:var(--bg3);border-radius:var(--r);padding:9px 11px;display:flex;justify-content:space-between;align-items:center"><span style="font-size:11px;color:var(--text2)">{k}</span><span style="font-family:\'Syne\',sans-serif;font-weight:800;font-size:15px;color:{cols[i%6]}">{v}</span></div>' for i,(k,v) in enumerate(top6))+"</div>"

    rec_rows="".join(f'<tr><td><span class="avsm" style="background:{dc(s["dept"])}22;color:{dc(s["dept"])}">{ini(s["name"])}</span><span class="tn">{s["name"]}</span></td><td><span class="bdg" style="background:{dc(s["dept"])}22;color:{dc(s["dept"])}">{s["dept"]}</span></td><td>{YM.get(s["year"],s["year"])}</td><td><span class="bdg" style="background:#6c63ff22;color:#8b84ff">{s["skill"]}</span></td></tr>' for s in students_data[-5:][::-1])
    roster="".join(f'<tr><td><span class="avsm" style="background:{dc(s["dept"])}22;color:{dc(s["dept"])}">{ini(s["name"])}</span><span class="tn">{s["name"]}</span></td><td><span class="bdg" style="background:{dc(s["dept"])}22;color:{dc(s["dept"])}">{s["dept"]}</span></td><td>{YM.get(s["year"],s["year"])}</td><td><span class="bdg" style="background:#6c63ff22;color:#8b84ff">{s["skill"]}</span></td><td><div class="pb {s["prof"].lower()}"><div class="bt"><div class="bf"></div></div><span style="font-size:10px;color:var(--text3)">{s["prof"]}</span></div></td></tr>' for s in students_data) or '<tr><td colspan="5"><div class="es"><div class="et">No students</div></div></td></tr>'
    tags_html="".join(f'<span class="tag" onclick="qs(\'{k}\')">{k}</span>' for k in sorted(sc,key=lambda x:-sc[x]))
    mx_sk=max((skct(s["name"]) for s in skills_data),default=1)
    sg="".join(f'<div class="sk-card"><div class="sk-top"><div class="sk-name">{sk["name"]}</div><span class="sk-cat" style="background:{cc(sk["cat"])}22;color:{cc(sk["cat"])}">{sk["cat"]}</span></div><div class="sk-num" style="color:{cc(sk["cat"])}">{skct(sk["name"])}</div><div class="sk-sub">{skct(sk["name"])} students</div><div class="sk-bar"><div class="sk-bar-inner" style="width:{skct(sk["name"])/mx_sk*100:.0f}%;background:{cc(sk["cat"])}"></div></div></div>' for sk in skills_data)
    proj_rows="".join(f'<tr><td class="tn">{p["title"]}</td><td><span class="bdg" style="background:{SC.get(p["status"],"#888")}22;color:{SC.get(p["status"],"#888")}">{p["status"]}</span></td><td style="font-size:10px;color:var(--text3)">{str(p.get("start_date",""))[:10]}</td><td style="font-size:10px;color:var(--text3)">{str(p.get("end_date",""))[:10]}</td></tr>' for p in projects_data) or '<tr><td colspan="4"><div class="es"><div class="et">No projects</div></div></td></tr>'
    task_rows="".join(f'<tr><td class="tn">{t["task_name"]}</td><td style="font-size:10px;color:var(--text2)">{t["project_title"]}</td><td style="font-size:10px;color:var(--text2)">{t["milestone_title"]}</td><td><span class="avsm" style="background:#6c63ff22;color:#8b84ff">{ini(t["student_name"])}</span>{t["student_name"]}</td><td><span class="bdg" style="background:{TC.get(t["status"],"#888")}22;color:{TC.get(t["status"],"#888")}">{t["status"]}</span></td></tr>' for t in tasks_data) or '<tr><td colspan="5"><div class="es"><div class="et">No tasks</div></div></td></tr>'
    def stars(r): return "".join("★" if i<(r or 0) else "☆" for i in range(5))
    rev_rows="".join(f'<tr><td class="tn">{rv["project_title"]}</td><td style="font-size:10px">{rv["reviewer"]}</td><td style="color:#ffd93d;letter-spacing:1px;font-size:11px">{stars(rv["rating"])}</td><td style="font-size:10px;color:var(--text2)">{(rv["comments"] or "")[:55]}{"..." if len(rv["comments"] or "")>55 else ""}</td></tr>' for rv in reviews_data) or '<tr><td colspan="4"><div class="es"><div class="et">No reviews</div></div></td></tr>'

    return f"""<link href="https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#0a0c10;--bg2:#111318;--bg3:#181b22;--bg4:#1e2130;--border:#ffffff12;--border2:#ffffff22;--text:#eef0f8;--text2:#8b91a8;--text3:#555b72;--accent:#6c63ff;--r:10px;--r2:16px}}
body,html{{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--text)}}
.shell{{display:grid;grid-template-columns:216px 1fr;min-height:100vh}}
.sidebar{{background:var(--bg2);border-right:1px solid var(--border);display:flex;flex-direction:column}}
.logo{{padding:17px 18px 15px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:9px}}
.logo-ico{{width:31px;height:31px;background:linear-gradient(135deg,#6c63ff,#4ecdc4);border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:12px;color:#fff;font-family:'Syne',sans-serif;flex-shrink:0}}
.logo-t{{font-family:'Syne',sans-serif;font-weight:700;font-size:12px}}.logo-s{{font-size:9px;color:var(--text3)}}
nav{{padding:8px 0;flex:1}}
.ni{{display:flex;align-items:center;gap:8px;padding:8px 18px;cursor:pointer;font-size:11px;color:var(--text2);border-left:2px solid transparent;transition:all .14s}}
.ni:hover{{background:var(--bg3);color:var(--text)}}.ni.on{{background:#6c63ff14;color:var(--text);border-left-color:#6c63ff}}
.ni svg{{width:13px;height:13px;flex-shrink:0;opacity:.7}}.ni.on svg{{opacity:1}}
.ni-g{{padding:5px 18px 1px;font-size:9px;color:var(--text3);text-transform:uppercase;letter-spacing:.08em;margin-top:3px}}
.sb-foot{{padding:12px 18px;border-top:1px solid var(--border)}}
.sb-stat{{display:flex;justify-content:space-between;font-size:10px;color:var(--text3);padding:2px 0}}
.sb-stat b{{color:#6c63ff;font-weight:500}}
.main{{display:flex;flex-direction:column}}
.topbar{{background:var(--bg2);border-bottom:1px solid var(--border);padding:0 24px;height:54px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:20}}
.pg-title{{font-family:'Syne',sans-serif;font-weight:700;font-size:14px}}.pg-crumb{{font-size:9px;color:var(--text3)}}
.qs{{background:var(--bg3);border:1px solid var(--border2);border-radius:var(--r);padding:6px 11px 6px 29px;color:var(--text);font-size:11px;width:190px;outline:none;font-family:'DM Sans',sans-serif}}
.qs::placeholder{{color:var(--text3)}}.qs-wrap{{position:relative}}.qs-ico{{position:absolute;left:8px;top:50%;transform:translateY(-50%);color:var(--text3)}}
.avt{{width:29px;height:29px;border-radius:50%;background:linear-gradient(135deg,#6c63ff,#4ecdc4);display:flex;align-items:center;justify-content:center;font-family:'Syne',sans-serif;font-weight:700;font-size:10px}}
.content{{padding:22px;flex:1}}
.sec{{display:none}}.sec.on{{display:block}}
@keyframes fi{{from{{opacity:0;transform:translateY(5px)}}to{{opacity:1;transform:translateY(0)}}}}.sec.on{{animation:fi .2s ease}}
.metrics{{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:11px;margin-bottom:16px}}
.mc{{background:var(--bg2);border:1px solid var(--border);border-radius:var(--r2);padding:14px;position:relative;overflow:hidden;transition:border-color .2s}}
.mc:hover{{border-color:var(--border2)}}
.mc-ico{{position:absolute;top:12px;right:12px;width:24px;height:24px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:12px}}
.mc.bl .mc-ico{{background:#6c63ff1a;color:#6c63ff}}.mc.tl .mc-ico{{background:#4ecdc41a;color:#4ecdc4}}.mc.gd .mc-ico{{background:#ffd93d1a;color:#ffd93d}}.mc.rd .mc-ico{{background:#ff6b6b1a;color:#ff6b6b}}.mc.gr .mc-ico{{background:#6bcb771a;color:#6bcb77}}.mc.pk .mc-ico{{background:#a78bfa1a;color:#a78bfa}}
.mc-lbl{{font-size:9px;color:var(--text3);text-transform:uppercase;letter-spacing:.07em;font-weight:500}}
.mc-val{{font-family:'Syne',sans-serif;font-weight:800;font-size:24px;margin:4px 0 2px}}.mc-note{{font-size:9px;color:var(--text3)}}
.panel{{background:var(--bg2);border:1px solid var(--border);border-radius:var(--r2);padding:18px;margin-bottom:14px}}
.ph{{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:14px;flex-wrap:wrap;gap:7px}}
.pt{{font-family:'Syne',sans-serif;font-weight:700;font-size:12px}}.ps{{font-size:9px;color:var(--text3);margin-top:1px}}
.pa{{display:flex;gap:6px;align-items:center;flex-wrap:wrap}}
.btn{{display:inline-flex;align-items:center;gap:5px;padding:5px 11px;border-radius:var(--r);font-size:10px;font-family:'DM Sans',sans-serif;cursor:pointer;transition:all .14s;border:none;font-weight:500}}
.bp{{background:#6c63ff;color:#fff}}.bp:hover{{background:#5a52e0}}
.bg2b{{background:transparent;color:var(--text2);border:1px solid var(--border2)}}.bg2b:hover{{background:var(--bg3);color:var(--text)}}
.fi{{display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap}}
.fin{{background:var(--bg3);border:1px solid var(--border2);border-radius:var(--r);padding:5px 9px;color:var(--text);font-size:10px;font-family:'DM Sans',sans-serif;outline:none}}
.fin::placeholder{{color:var(--text3)}}select.fin option{{background:var(--bg3);color:var(--text)}}
.tw{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse}}
th{{font-size:9px;color:var(--text3);text-transform:uppercase;letter-spacing:.06em;padding:0 11px 8px;text-align:left;border-bottom:1px solid var(--border)}}
td{{padding:10px 11px;font-size:10px;color:var(--text2);border-bottom:1px solid var(--border);transition:background .1s}}
tr:hover td{{background:var(--bg3);color:var(--text)}}tr:last-child td{{border:none}}
.tn{{color:var(--text);font-weight:500;font-family:'Syne',sans-serif;font-size:10px}}
.avsm{{width:24px;height:24px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:8px;font-weight:700;font-family:'Syne',sans-serif;margin-right:5px;vertical-align:middle;flex-shrink:0}}
.bdg{{display:inline-flex;align-items:center;padding:2px 7px;border-radius:100px;font-size:9px;font-weight:500}}
.pb{{display:flex;align-items:center;gap:6px}}.bt{{flex:1;height:3px;background:var(--bg4);border-radius:2px;overflow:hidden;min-width:44px}}.bf{{height:100%;border-radius:2px}}
.beginner .bf{{width:30%;background:#ff6b6b}}.intermediate .bf{{width:65%;background:#ffd93d}}.advanced .bf{{width:100%;background:#6bcb77}}
.es{{text-align:center;padding:32px 20px}}.ei{{font-size:32px;opacity:.2;margin-bottom:9px}}.et{{font-size:11px;color:var(--text3)}}
.skill-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:11px}}
.sk-card{{background:var(--bg3);border:1px solid var(--border);border-radius:var(--r2);padding:13px}}
.sk-top{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:7px}}
.sk-name{{font-family:'Syne',sans-serif;font-weight:700;font-size:11px;color:var(--text)}}.sk-cat{{font-size:9px;padding:2px 6px;border-radius:100px}}
.sk-num{{font-family:'Syne',sans-serif;font-weight:800;font-size:20px;margin-bottom:2px}}.sk-sub{{font-size:9px;color:var(--text3);margin-bottom:6px}}
.sk-bar{{height:3px;background:var(--bg4);border-radius:2px;overflow:hidden}}.sk-bar-inner{{height:100%;border-radius:2px}}
.dept-bars{{display:flex;flex-direction:column;gap:8px}}
.db-row{{display:flex;align-items:center;gap:8px}}.db-lbl{{width:66px;font-size:9px;color:var(--text3);text-align:right;flex-shrink:0}}
.db-track{{flex:1;background:var(--bg4);height:16px;border-radius:var(--r);overflow:hidden}}
.db-inner{{height:100%;border-radius:var(--r);display:flex;align-items:center;padding-left:6px;font-size:8px;font-weight:700;font-family:'Syne',sans-serif}}
.db-ct{{font-size:9px;color:var(--text3);width:16px;text-align:right;flex-shrink:0}}
.tag-row{{display:flex;flex-wrap:wrap;gap:5px;margin:6px 0 12px}}
.tag{{padding:3px 9px;border-radius:100px;font-size:9px;cursor:pointer;border:1px solid var(--border2);color:var(--text2);background:var(--bg3)}}
.tag:hover{{background:var(--accent);color:#fff;border-color:var(--accent)}}
.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px}}
.prog-wrap{{background:var(--bg4);border-radius:3px;height:5px;overflow:hidden;margin-top:4px}}
.prog-fill{{height:100%;border-radius:3px;background:linear-gradient(90deg,#6c63ff,#4ecdc4)}}
.toast-area{{position:fixed;top:12px;right:12px;z-index:9999;display:flex;flex-direction:column;gap:6px;pointer-events:none}}
.toast{{background:var(--bg2);border:1px solid var(--border2);border-radius:var(--r2);padding:9px 13px;font-size:10px;color:var(--text);display:flex;align-items:center;gap:8px;transform:translateX(110%);transition:transform .22s ease;min-width:200px;pointer-events:all}}
.toast.show{{transform:translateX(0)}}.toast.ok{{border-color:#6bcb7750}}.toast.err{{border-color:#ff6b6b50}}.toast.inf{{border-color:#6c63ff50}}
.tdot{{width:5px;height:5px;border-radius:50%;flex-shrink:0}}
.toast.ok .tdot{{background:#6bcb77}}.toast.err .tdot{{background:#ff6b6b}}.toast.inf .tdot{{background:#6c63ff}}
</style>

<div class="shell">
<aside class="sidebar">
  <div class="logo">
    <div class="logo-ico">CT</div>
    <div><div class="logo-t">CampusTalent</div><div class="logo-s">Management System</div></div>
  </div>
  <nav>
    <div class="ni-g">Overview</div>
    <div class="ni on" onclick="go('dash',this)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>Dashboard</div>
    <div class="ni-g">Students</div>
    <div class="ni" onclick="go('search',this)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="11" cy="11" r="7"/><path d="m16.5 16.5 4 4"/></svg>Search Talent</div>
    <div class="ni" onclick="go('students',this)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>All Students</div>
    <div class="ni-g">Projects</div>
    <div class="ni" onclick="go('projects',this)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>Projects</div>
    <div class="ni" onclick="go('tasks',this)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>Tasks</div>
    <div class="ni" onclick="go('reviews',this)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>Reviews</div>
    <div class="ni-g">Skills</div>
    <div class="ni" onclick="go('skills',this)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/></svg>Skills Manager</div>
  </nav>
  <div class="sb-foot">
    <div class="sb-stat">Students <b>{total_students}</b></div>
    <div class="sb-stat">Projects <b>{total_projects}</b></div>
    <div class="sb-stat">Skills <b>{total_skills}</b></div>
    <div class="sb-stat">Tasks Done <b>{done_tasks}/{total_tasks}</b></div>
  </div>
</aside>

<div class="main">
  <div class="topbar">
    <div><div class="pg-title" id="pg-t">Dashboard</div><div class="pg-crumb" id="pg-c">CampusTalent / Overview</div></div>
    <div style="display:flex;align-items:center;gap:8px">
      <div class="qs-wrap">
        <svg class="qs-ico" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m16.5 16.5 4 4"/></svg>
        <input class="qs" placeholder="Search skill..." oninput="gSearch(this.value)">
      </div>
      <div class="avt">AD</div>
    </div>
  </div>

  <div class="content">

    <div id="s-dash" class="sec on">
      <div class="metrics">
        <div class="mc bl"><div class="mc-ico">👥</div><div class="mc-lbl">Students</div><div class="mc-val">{total_students}</div><div class="mc-note">Enrolled</div></div>
        <div class="mc tl"><div class="mc-ico">✦</div><div class="mc-lbl">Skills</div><div class="mc-val">{total_skills}</div><div class="mc-note">Tracked</div></div>
        <div class="mc gd"><div class="mc-ico">📁</div><div class="mc-lbl">Projects</div><div class="mc-val">{total_projects}</div><div class="mc-note">{active_proj} active</div></div>
        <div class="mc rd"><div class="mc-ico">⚡</div><div class="mc-lbl">Advanced</div><div class="mc-val">{adv}</div><div class="mc-note">Top talent</div></div>
        <div class="mc gr"><div class="mc-ico">✅</div><div class="mc-lbl">Tasks Done</div><div class="mc-val">{done_tasks}</div><div class="mc-note">of {total_tasks}</div></div>
        <div class="mc pk"><div class="mc-ico">📊</div><div class="mc-lbl">Completion</div><div class="mc-val">{task_pct}%</div><div class="prog-wrap" style="margin-top:5px"><div class="prog-fill" style="width:{task_pct}%"></div></div></div>
      </div>
      <div class="two-col">
        <div class="panel"><div class="ph"><div><div class="pt">Dept Distribution</div></div></div><div class="dept-bars">{dept_html}</div></div>
        <div class="panel"><div class="ph"><div><div class="pt">Top Skills</div></div></div>{top_html}</div>
      </div>
      <div class="panel">
        <div class="ph"><div><div class="pt">Recent Enrollments</div></div><button class="btn bg2b" onclick="go('students',document.querySelectorAll('.ni')[3])">View All</button></div>
        <div class="tw"><table><thead><tr><th>Student</th><th>Dept</th><th>Year</th><th>Skill</th></tr></thead><tbody>{rec_rows}</tbody></table></div>
      </div>
    </div>

    <div id="s-search" class="sec">
      <div class="panel">
        <div class="ph"><div><div class="pt">Find Talent by Skill</div></div></div>
        <div class="fi">
          <input class="fin" id="sk-q" placeholder="e.g. Python..." oninput="doSearch()" style="flex:1;min-width:130px">
          <select class="fin" id="f-dept" onchange="doSearch()"><option value="">All Depts</option><option>AI/ML</option><option>CS</option><option>IT</option><option>EC</option><option>Mechanical</option></select>
          <select class="fin" id="f-prof" onchange="doSearch()"><option value="">All Levels</option><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select>
          <select class="fin" id="f-year" onchange="doSearch()"><option value="">All Years</option><option value="1">1st</option><option value="2">2nd</option><option value="3">3rd</option><option value="4">4th</option></select>
        </div>
        <div class="tag-row">{tags_html}</div>
        <div id="search-out"><div class="es"><div class="ei">🔍</div><div class="et">Type a skill or click a tag</div></div></div>
      </div>
    </div>

    <div id="s-students" class="sec">
      <div class="panel">
        <div class="ph">
          <div><div class="pt">Student Roster</div><div class="ps" id="roster-ps">{total_students} students</div></div>
          <div class="pa">
            <select class="fin" id="r-dept" onchange="filterRoster()"><option value="">All Depts</option><option>AI/ML</option><option>CS</option><option>IT</option><option>EC</option><option>Mechanical</option></select>
            <select class="fin" id="r-year" onchange="filterRoster()"><option value="">All Years</option><option value="1">1st</option><option value="2">2nd</option><option value="3">3rd</option><option value="4">4th</option></select>
            <select class="fin" id="r-prof" onchange="filterRoster()"><option value="">All Levels</option><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select>
          </div>
        </div>
        <div class="tw"><table><thead><tr><th>Student</th><th>Dept</th><th>Year</th><th>Skill</th><th>Level</th></tr></thead><tbody id="roster-tbl">{roster}</tbody></table></div>
      </div>
    </div>

    <div id="s-projects" class="sec">
      <div class="panel">
        <div class="ph"><div><div class="pt">All Projects</div><div class="ps">{total_projects} total · {active_proj} active</div></div></div>
        <div class="tw"><table><thead><tr><th>Title</th><th>Status</th><th>Start</th><th>End</th></tr></thead><tbody>{proj_rows}</tbody></table></div>
      </div>
    </div>

    <div id="s-tasks" class="sec">
      <div class="panel">
        <div class="ph">
          <div><div class="pt">Task Allocation</div><div class="ps">{done_tasks} done · {total_tasks-done_tasks} pending</div></div>
          <div class="pa"><select class="fin" id="t-status" onchange="filterTasks()"><option value="">All Statuses</option><option>To Do</option><option>In Progress</option><option>Done</option><option>Blocked</option></select></div>
        </div>
        <div class="tw"><table><thead><tr><th>Task</th><th>Project</th><th>Milestone</th><th>Assigned To</th><th>Status</th></tr></thead><tbody id="tasks-tbl">{task_rows}</tbody></table></div>
      </div>
    </div>

    <div id="s-reviews" class="sec">
      <div class="panel">
        <div class="ph"><div><div class="pt">Project Reviews</div></div></div>
        <div class="tw"><table><thead><tr><th>Project</th><th>Reviewer</th><th>Rating</th><th>Comments</th></tr></thead><tbody>{rev_rows}</tbody></table></div>
      </div>
    </div>

    <div id="s-skills" class="sec">
      <div class="panel">
        <div class="ph">
          <div><div class="pt">Skills Manager</div><div class="ps">{total_skills} skills</div></div>
          <div class="pa"><select class="fin" id="skm-cat" onchange="filterSkills()"><option value="">All Categories</option><option>Programming</option><option>Framework</option><option>Database</option><option>Design</option><option>Hardware</option><option>Other</option></select></div>
        </div>
        <div class="skill-grid" id="skill-grid">{sg}</div>
      </div>
    </div>

  </div>
</div>
</div>
<div class="toast-area" id="toasts"></div>

<script>
const DC={{CS:'#6c63ff','AI/ML':'#4ecdc4',IT:'#ffd93d',EC:'#ff6b6b',Mechanical:'#6bcb77'}};
const YM={{1:'1st',2:'2nd',3:'3rd',4:'4th'}};
const TC={{'To Do':'#8b91a8','In Progress':'#ffd93d','Done':'#6bcb77','Blocked':'#ff6b6b'}};
const CC={{Programming:'#6c63ff',Framework:'#4ecdc4',Database:'#ffd93d',Design:'#ff6b6b',Hardware:'#6bcb77',Other:'#a78bfa'}};
const allStudents={js_stu};
const allSkills={js_sk};
const allTasks={js_tasks};
function ini(n){{return(n||'').split(' ').map(x=>x[0]||'').join('').toUpperCase().slice(0,2)||'??'}}
function dc(d){{return DC[d]||'#888'}}
function toast(msg,type='ok'){{
  const el=document.createElement('div');el.className='toast '+type;
  el.innerHTML=`<div class="tdot"></div><span>${{msg}}</span>`;
  document.getElementById('toasts').appendChild(el);
  requestAnimationFrame(()=>requestAnimationFrame(()=>el.classList.add('show')));
  setTimeout(()=>{{el.classList.remove('show');setTimeout(()=>el.remove(),320)}},2500);
}}
function go(id,el){{
  document.querySelectorAll('.ni').forEach(n=>n.classList.remove('on'));
  if(el){{const nav=el.classList.contains('ni')?el:el.closest('.ni');if(nav)nav.classList.add('on');}}
  document.querySelectorAll('.sec').forEach(s=>s.classList.remove('on'));
  document.getElementById('s-'+id).classList.add('on');
  const T={{dash:'Dashboard',search:'Search Talent',students:'All Students',projects:'Projects',tasks:'Tasks',reviews:'Reviews',skills:'Skills Manager'}};
  const C={{dash:'Overview',search:'Search',students:'Roster',projects:'Projects',tasks:'Tasks',reviews:'Reviews',skills:'Skills'}};
  document.getElementById('pg-t').textContent=T[id]||id;
  document.getElementById('pg-c').textContent='CampusTalent / '+(C[id]||id);
}}
function filterRoster(){{
  const dF=document.getElementById('r-dept').value,yF=document.getElementById('r-year').value,pF=document.getElementById('r-prof').value;
  let list=allStudents.filter(s=>(!dF||s.dept===dF)&&(!yF||s.year==yF)&&(!pF||s.prof===pF));
  document.getElementById('roster-ps').textContent=`Showing ${{list.length}} of ${{allStudents.length}} students`;
  document.getElementById('roster-tbl').innerHTML=list.length?list.map(s=>`<tr>
    <td><span class="avsm" style="background:${{dc(s.dept)}}22;color:${{dc(s.dept)}}">${{ini(s.name)}}</span><span class="tn">${{s.name}}</span></td>
    <td><span class="bdg" style="background:${{dc(s.dept)}}22;color:${{dc(s.dept)}}">${{s.dept}}</span></td>
    <td>${{YM[s.year]||s.year}}</td><td><span class="bdg" style="background:#6c63ff22;color:#8b84ff">${{s.skill}}</span></td>
    <td><div class="pb ${{s.prof.toLowerCase()}}"><div class="bt"><div class="bf"></div></div><span style="font-size:9px;color:var(--text3)">${{s.prof}}</span></div></td>
  </tr>`).join(''):`<tr><td colspan="5"><div class="es"><div class="et">No matches</div></div></td></tr>`;
}}
function filterTasks(){{
  const sF=document.getElementById('t-status').value;
  let list=allTasks.filter(t=>!sF||t.status===sF);
  document.getElementById('tasks-tbl').innerHTML=list.length?list.map(t=>`<tr>
    <td class="tn">${{t.task_name}}</td><td style="font-size:9px;color:var(--text2)">${{t.project_title}}</td>
    <td style="font-size:9px;color:var(--text2)">${{t.milestone_title}}</td>
    <td><span class="avsm" style="background:#6c63ff22;color:#8b84ff">${{ini(t.student_name)}}</span>${{t.student_name}}</td>
    <td><span class="bdg" style="background:${{(TC[t.status]||'#888')}}22;color:${{TC[t.status]||'#888'}}">${{t.status}}</span></td>
  </tr>`).join(''):`<tr><td colspan="5"><div class="es"><div class="et">No tasks</div></div></td></tr>`;
}}
function qs(sk){{document.getElementById('sk-q').value=sk;doSearch();}}
function doSearch(){{
  const q2=document.getElementById('sk-q').value.trim().toLowerCase();
  const dF=document.getElementById('f-dept').value,pF=document.getElementById('f-prof').value,yF=document.getElementById('f-year').value;
  if(!q2){{document.getElementById('search-out').innerHTML=`<div class="es"><div class="ei">🔍</div><div class="et">Type a skill</div></div>`;return;}}
  let r=allStudents.filter(s=>s.skill.toLowerCase().includes(q2)&&(!dF||s.dept===dF)&&(!pF||s.prof===pF)&&(!yF||s.year==yF));
  if(!r.length){{document.getElementById('search-out').innerHTML=`<div class="es"><div class="ei">🎯</div><div class="et">No results for "${{q2}}"</div></div>`;return;}}
  document.getElementById('search-out').innerHTML=`<div style="font-size:10px;color:var(--text3);margin-bottom:9px">${{r.length}} result(s)</div>
    <div class="tw"><table><thead><tr><th>Student</th><th>Dept</th><th>Year</th><th>Skill</th><th>Level</th><th>Email</th></tr></thead>
    <tbody>${{r.map(s=>`<tr>
      <td><span class="avsm" style="background:${{dc(s.dept)}}22;color:${{dc(s.dept)}}">${{ini(s.name)}}</span><span class="tn">${{s.name}}</span></td>
      <td><span class="bdg" style="background:${{dc(s.dept)}}22;color:${{dc(s.dept)}}">${{s.dept}}</span></td>
      <td>${{YM[s.year]||s.year}}</td><td><span class="bdg" style="background:#6c63ff22;color:#8b84ff">${{s.skill}}</span></td>
      <td><div class="pb ${{s.prof.toLowerCase()}}"><div class="bt"><div class="bf"></div></div><span style="font-size:9px;color:var(--text3)">${{s.prof}}</span></div></td>
      <td style="color:#6c63ff;font-size:9px">${{s.email||'—'}}</td>
    </tr>`).join('')}}</tbody></table></div>`;
}}
function gSearch(v){{if(!v.trim())return;go('search',document.querySelectorAll('.ni')[2]);document.getElementById('sk-q').value=v;doSearch();}}
function filterSkills(){{
  const catF=document.getElementById('skm-cat').value;
  const stuCounts={{}};allStudents.forEach(s=>stuCounts[s.skill]=(stuCounts[s.skill]||0)+1);
  const list=catF?allSkills.filter(s=>s.cat===catF):allSkills;
  const maxC=Math.max(...allSkills.map(s=>stuCounts[s.name]||0),1);
  document.getElementById('skill-grid').innerHTML=list.map(sk=>{{
    const ct=stuCounts[sk.name]||0,col=CC[sk.cat]||'#888';
    return`<div class="sk-card"><div class="sk-top"><div class="sk-name">${{sk.name}}</div><span class="sk-cat" style="background:${{col}}22;color:${{col}}">${{sk.cat}}</span></div>
    <div class="sk-num" style="color:${{col}}">${{ct}}</div><div class="sk-sub">${{ct}} students</div>
    <div class="sk-bar"><div class="sk-bar-inner" style="width:${{ct/maxC*100}}%;background:${{col}}"></div></div></div>`;
  }}).join('');
}}
</script>"""

# ─── RENDER ───────────────────────────────────────────────────────────────────
students_data = fetch_students()
skills_data   = fetch_skills()
projects_data = fetch_projects()
tasks_data    = fetch_tasks()
reviews_data  = fetch_reviews()
endorsements  = fetch_endorsements()
milestones    = fetch_milestones()

st.components.v1.html(
    build_html(students_data, skills_data, projects_data, tasks_data, reviews_data),
    height=880, scrolling=True
)

# ─── STREAMLIT CRUD FORMS ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### ⚙️ Manage Data")

skill_names = [s["name"] for s in skills_data] or ["No skills"]
skill_map   = {s["name"]: s["id"] for s in skills_data}
stu_map     = {f"{s['name']} ({s['dept']})": s["id"] for s in students_data}
proj_map    = {p["title"]: p["id"] for p in projects_data}
ms_map      = {f"{m['project_title']} → {m['title']}": m["id"] for m in milestones}

tabs = st.tabs(["➕ Student","🗑 Del Student","📁 Project","🗑 Del Project",
                "🏁 Milestone","✅ Task","⭐ Endorsement","📝 Review","🌟 Skill","🗑 Del Skill"])

# ADD STUDENT
with tabs[0]:
    with st.form("add_stu"):
        c1,c2,c3 = st.columns(3)
        name  = c1.text_input("Full Name *")
        dept  = c2.selectbox("Department", ["AI/ML","CS","IT","EC","Mechanical"])
        year  = c3.selectbox("Year",[1,2,3,4], format_func=lambda x:f"{x}{'st'if x==1 else'nd'if x==2 else'rd'if x==3 else'th'} Year")
        c4,c5,c6 = st.columns(3)
        skill = c4.selectbox("Primary Skill", skill_names)
        prof  = c5.selectbox("Proficiency",["Beginner","Intermediate","Advanced"])
        email = c6.text_input("Email (optional)")
        if st.form_submit_button("✅ Enroll Student", type="primary"):
            if name.strip():
                sid = run("INSERT INTO Students (Name,Department,Year,Email) VALUES (%s,%s,%s,%s)",(name.strip(),dept,year,email))
                if sid: run("INSERT INTO StudentSkills (StudentID,SkillID,Proficiency) VALUES (%s,%s,%s)",(sid,skill_map.get(skill,1),prof))
                st.success(f"✅ {name} enrolled!"); st.rerun()
            else: st.warning("Name required.")

# DELETE STUDENT
with tabs[1]:
    if stu_map:
        pick = st.selectbox("Select student", list(stu_map.keys()))
        st.warning("⚠️ Also removes their tasks, memberships, endorsements and skills.")
        if st.button("🗑️ Delete Student", type="primary"):
            sid = stu_map[pick]
            run("DELETE FROM Task_Allocation WHERE StudentID=%s",(sid,))
            run("DELETE FROM Project_Members WHERE StudentID=%s",(sid,))
            run("DELETE FROM Skill_Endorsements WHERE StudentID=%s OR EndorserID=%s",(sid,sid))
            run("DELETE FROM StudentSkills WHERE StudentID=%s",(sid,))
            run("DELETE FROM Students WHERE StudentID=%s",(sid,))
            st.success(f"Deleted {pick}"); st.rerun()
    else: st.info("No students.")

# ADD PROJECT
with tabs[2]:
    with st.form("add_proj"):
        c1,c2 = st.columns(2)
        title  = c1.text_input("Project Title *")
        status = c2.selectbox("Status",["Planning","Active","Completed","On Hold"])
        descr  = st.text_area("Description", height=70)
        c3,c4  = st.columns(2)
        sdate  = c3.date_input("Start Date", value=date.today())
        edate  = c4.date_input("End Date",   value=date.today())
        req_skills = st.multiselect("Required Skills", skill_names)
        members    = st.multiselect("Add Members",     list(stu_map.keys()))
        if st.form_submit_button("✅ Create Project", type="primary"):
            if title.strip():
                pid = run("INSERT INTO Projects (Title,Description,Status,StartDate,EndDate) VALUES (%s,%s,%s,%s,%s)",(title,descr,status,sdate,edate))
                for sk in req_skills:
                    run("INSERT IGNORE INTO Project_Requirements (ProjectID,SkillID,Importance) VALUES (%s,%s,'Required')",(pid,skill_map[sk]))
                for m in members:
                    run("INSERT IGNORE INTO Project_Members (ProjectID,StudentID,Role,JoinedDate) VALUES (%s,%s,'Member',%s)",(pid,stu_map[m],date.today()))
                st.success(f"✅ '{title}' created!"); st.rerun()
            else: st.warning("Title required.")

# DELETE PROJECT
with tabs[3]:
    if proj_map:
        pick = st.selectbox("Select project", list(proj_map.keys()))
        st.warning("⚠️ Deletes all milestones, tasks, members, requirements and reviews.")
        if st.button("🗑️ Delete Project", type="primary"):
            pid = proj_map[pick]
            run("DELETE FROM Task_Allocation WHERE MilestoneID IN (SELECT MilestoneID FROM Milestones WHERE ProjectID=%s)",(pid,))
            run("DELETE FROM Milestones WHERE ProjectID=%s",(pid,))
            run("DELETE FROM Project_Members WHERE ProjectID=%s",(pid,))
            run("DELETE FROM Project_Requirements WHERE ProjectID=%s",(pid,))
            run("DELETE FROM Project_Reviews WHERE ProjectID=%s",(pid,))
            run("DELETE FROM Projects WHERE ProjectID=%s",(pid,))
            st.success(f"Deleted '{pick}'"); st.rerun()
    else: st.info("No projects.")

# ADD MILESTONE
with tabs[4]:
    if proj_map:
        with st.form("add_ms"):
            c1,c2 = st.columns(2)
            ms_proj  = c1.selectbox("Project", list(proj_map.keys()))
            ms_stat  = c2.selectbox("Status",["Pending","In Progress","Completed"])
            ms_title = st.text_input("Milestone Title *")
            ms_dl    = st.date_input("Deadline", value=date.today())
            if st.form_submit_button("✅ Add Milestone", type="primary"):
                if ms_title.strip():
                    run("INSERT INTO Milestones (ProjectID,Title,Deadline,Status) VALUES (%s,%s,%s,%s)",(proj_map[ms_proj],ms_title,ms_dl,ms_stat))
                    st.success("✅ Milestone added!"); st.rerun()
                else: st.warning("Title required.")
    else: st.info("Create a project first.")

# ADD TASK
with tabs[5]:
    if ms_map and stu_map:
        with st.form("add_task"):
            c1,c2  = st.columns(2)
            t_ms   = c1.selectbox("Milestone", list(ms_map.keys()))
            t_stu  = c2.selectbox("Assign To",  list(stu_map.keys()))
            t_name = st.text_input("Task Name *")
            t_stat = st.selectbox("Status",["To Do","In Progress","Done","Blocked"])
            if st.form_submit_button("✅ Add Task", type="primary"):
                if t_name.strip():
                    run("INSERT INTO Task_Allocation (MilestoneID,StudentID,TaskName,TaskStatus) VALUES (%s,%s,%s,%s)",(ms_map[t_ms],stu_map[t_stu],t_name,t_stat))
                    st.success("✅ Task assigned!"); st.rerun()
                else: st.warning("Task name required.")
    else: st.info("Need milestones and students first.")

# ADD ENDORSEMENT
with tabs[6]:
    if stu_map and skill_map:
        with st.form("add_end"):
            c1,c2,c3 = st.columns(3)
            e_stu = c1.selectbox("Student (receives)", list(stu_map.keys()))
            e_sk  = c2.selectbox("Skill",              skill_names)
            e_end = c3.selectbox("Endorser",           list(stu_map.keys()))
            if st.form_submit_button("⭐ Add Endorsement", type="primary"):
                if stu_map[e_stu] != stu_map[e_end]:
                    run("INSERT INTO Skill_Endorsements (StudentID,SkillID,EndorserID,EndorsedDate) VALUES (%s,%s,%s,%s)",(stu_map[e_stu],skill_map[e_sk],stu_map[e_end],date.today()))
                    st.success("✅ Endorsement recorded!"); st.rerun()
                else: st.warning("Student and endorser must be different.")
        if endorsements:
            st.markdown("**Recent**")
            st.dataframe(pd.DataFrame(endorsements).head(8), use_container_width=True)
    else: st.info("Need students and skills first.")

# ADD REVIEW
with tabs[7]:
    if proj_map:
        with st.form("add_rev"):
            c1,c2,c3 = st.columns(3)
            r_proj = c1.selectbox("Project", list(proj_map.keys()))
            r_name = c2.text_input("Reviewer Name")
            r_rat  = c3.selectbox("Rating ⭐",[5,4,3,2,1])
            r_com  = st.text_area("Comments", height=70)
            if st.form_submit_button("📝 Submit Review", type="primary"):
                run("INSERT INTO Project_Reviews (ProjectID,ReviewerName,Rating,Comments,ReviewDate) VALUES (%s,%s,%s,%s,%s)",(proj_map[r_proj],r_name,r_rat,r_com,date.today()))
                st.success("✅ Review submitted!"); st.rerun()
    else: st.info("No projects yet.")

# ADD SKILL
with tabs[8]:
    with st.form("add_sk"):
        c1,c2,c3 = st.columns(3)
        sk_name = c1.text_input("Skill Name *")
        sk_cat  = c2.selectbox("Category",["Programming","Framework","Database","Design","Hardware","Other"])
        sk_diff = c3.selectbox("Difficulty",["Easy","Medium","Hard"])
        sk_desc = st.text_input("Description (optional)")
        if st.form_submit_button("✅ Add Skill", type="primary"):
            if sk_name.strip():
                run("INSERT INTO Skills (SkillName,Category,Difficulty,Description) VALUES (%s,%s,%s,%s)",(sk_name.strip(),sk_cat,sk_diff,sk_desc))
                st.success(f"✅ '{sk_name}' added!"); st.rerun()
            else: st.warning("Name required.")

# DELETE SKILL
with tabs[9]:
    if skill_map:
        sk_pick = st.selectbox("Select skill to delete", list(skill_map.keys()))
        st.warning("⚠️ Removes skill from all student profiles, endorsements and project requirements.")
        if st.button("🗑️ Delete Skill", type="primary"):
            sid = skill_map[sk_pick]
            run("DELETE FROM Skill_Endorsements WHERE SkillID=%s",(sid,))
            run("DELETE FROM Project_Requirements WHERE SkillID=%s",(sid,))
            run("DELETE FROM StudentSkills WHERE SkillID=%s",(sid,))
            run("DELETE FROM Skills WHERE SkillID=%s",(sid,))
            st.success(f"Deleted '{sk_pick}'"); st.rerun()
    else: st.info("No skills.")