#!/usr/bin/env python3
# ============================================
# SCRAPER 2.0 TG — SESSION-BASED | NO API INPUT
# Created by Saeka Tojirp
# Auto-Login | Glitch+Glow | Full Animation
# TXT Deep Extract | Live Monitor | Scroll Logs
# ============================================
import re, os, sys, asyncio, requests, time, shutil, subprocess, importlib, json

# ── AUTO-SETUP ────────────────────────────
def auto_setup():
    packages = {"telethon": "telethon", "requests": "requests", "bs4": "beautifulsoup4"}
    for mod, pkg in packages.items():
        try:
            importlib.import_module(mod)
        except ImportError:
            print(f"\033[1;33m [*] Installing {pkg}...\033[0m")
            subprocess.run([sys.executable, "-m", "pip", "install", pkg], capture_output=True)
    bashrc = os.path.expanduser("~/.bashrc")
    alias_line = "alias tgscrape='python3 ~/scraper.py'"
    if not os.path.exists(bashrc) or alias_line not in open(bashrc).read():
        os.system(f"echo \"{alias_line}\" >> {bashrc}")
auto_setup()
from bs4 import BeautifulSoup
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaDocument

# ── BUILT-IN API ─────────────────────────
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
SESSION_FILE = os.path.expanduser("~/.prvtspy_session")

# ── COLORS ────────────────────────────────
R='\033[91m'; G='\033[92m'; Y='\033[93m'; B='\033[94m'
M='\033[95m'; C='\033[96m'; W='\033[97m'
BOLD='\033[1m'; DIM='\033[2m'; RES='\033[0m'

def term_width():
    try: return shutil.get_terminal_size().columns
    except: return 60

# ── ANIMATIONS ────────────────────────────
def spinner(text="Loading", sec=1.5):
    frames=['◜','◠','◝','◞','◡','◟']
    end=time.time()+sec; i=0
    while time.time()<end:
        sys.stdout.write(f"\r  {C}{frames[i%6]} {RES}{text}...")
        sys.stdout.flush(); time.sleep(0.1); i+=1
    sys.stdout.write("\r"+" "*40+"\r")

def progress_bar(current, total, label="Scraping"):
    if total<=0: return
    pct = (current*100)//total
    bar_len = 35
    filled = (current*bar_len)//total
    bar = f"{G}{'█'*filled}{DIM}{'░'*(bar_len-filled)}{RES}"
    sys.stdout.write(f"\r  {label}: |{bar}| {pct}%")
    sys.stdout.flush()
    if current == total: sys.stdout.write("\n")

def pulse_glow(text, times=3, delay=0.3):
    for _ in range(times):
        sys.stdout.write(f"\r  {G}{BOLD}{text}{RES}")
        sys.stdout.flush(); time.sleep(delay/2)
        sys.stdout.write(f"\r  {DIM}{text}{RES}")
        sys.stdout.flush(); time.sleep(delay/2)
    sys.stdout.write(f"\r  {G}{BOLD}{text}{RES}\n")

def glide_text(text, delay=0.03):
    for c in text:
        sys.stdout.write(f"{G}{c}{RES}"); sys.stdout.flush(); time.sleep(delay)
    print()

def notify(icon, msg, color=G):
    print(f"  [{color}{icon}{RES}] {msg}")

# ── BANNER (Created by Saeka Tojirp) ──────
def banner():
    os.system('clear')
    w = term_width()
    title = "SCRAPER 2.0 TG"
    creator = "Created by Saeka Tojirp"
    # Glitch layers
    sys.stdout.write(f"{R}{BOLD}  {title}  {RES}\n"); sys.stdout.flush(); time.sleep(0.04)
    sys.stdout.write(f"{B}{BOLD}  {title}  {RES}\n"); sys.stdout.flush(); time.sleep(0.04)
    sys.stdout.write(f"{G}{BOLD}  {title}  {RES}\n"); sys.stdout.flush(); time.sleep(0.02)
    print(f"{DIM}  {creator}{RES}")
    print(f"{C}  {'─'*w}{RES}")
    print()

# ── PATTERNS (DEEP EXTRACT) ──────────────
PATTERNS={
    "ssh":r"ssh://[^\s]+","vmess":r"vmess://[^\s]+","vless":r"vless://[^\s]+",
    "trojan":r"trojan://[^\s]+","ssr":r"ssr://[^\s]+","ss":r"ss://[^\s]+",
    "hysteria":r"hysteria://[^\s]+","tuic":r"tuic://[^\s]+",
    "http_custom":r"(?:server|proxy|host)\s*[:=]\s*[^\s]+",
    "payload":r"(?:GET|POST|CONNECT|PUT|HEAD)\s+[^\s]+\s+HTTP/\d\.\d",
    "sni":r"(?:SNI|sni|bug)\s*[:=]\s*[^\s]+",
    "run_app":r"[a-zA-Z0-9\-]+\.run\.app",
    "ip_port":r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+",
}

def extract(text, scrape_mode="all"):
    found={}
    for n,p in PATTERNS.items():
        if scrape_mode=="config" and n in ("sni","ip_port","payload","run_app"): continue
        if scrape_mode=="text" and n in ("vmess","vless","trojan","ssh","ssr","ss"): continue
        if scrape_mode=="runapp" and n!="run_app": continue
        m=re.findall(p,text,re.I)
        if m: found[n]=list(set(m))
    return found

def bless(t,c):
    if t in ["vmess","vless","trojan","ssh","ss","ssr","hysteria","tuic"]:
        return c.startswith(f"{t}://")
    return True

def save_configs(configs,filename="blessed_configs.txt"):
    with open(filename,"a",encoding="utf-8") as f:
        for c in configs:
            status="BLESSED" if c['blessed'] else "RAW"
            f.write(f"[{c['type'].upper()}] [{status}] {c['channel']}\n{c['config']}\n{'-'*40}\n")

# ── TXT DEEP EXTRACT ──────────────────────
async def download_txt(message, prefix="temp"):
    if not message.media: return ""
    doc = getattr(message.media, 'document', None)
    if not doc: return ""
    is_txt = doc.mime_type == "text/plain" or any(
        getattr(a, 'file_name', '').endswith(('.txt','.log','.cfg','.conf'))
        for a in doc.attributes if hasattr(a, 'file_name'))
    if not is_txt: return ""
    fname = f"_{prefix}_dl.txt"
    try:
        await message.download_media(file=fname)
        with open(fname, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        os.remove(fname)
        return content
    except: return ""

# ── SESSION MANAGER ──────────────────────
async def detect_login():
    """Return True if session exists and is valid."""
    if not os.path.exists(SESSION_FILE): return False
    try:
        client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        await client.start()
        await client.disconnect()
        return True
    except: return False

async def create_session():
    if await detect_login():
        client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        await client.start()
        me = await client.get_me()
        print(f"\n  {G}[WELCOME]{RES} {me.first_name} (@{me.username})")
        await client.disconnect()
        return True
    print(f"\n  {Y}[!]{RES} No session found. Login required (one-time only).")
    phone = input(f"  {Y}[?]{RES} Phone number (+63...): ").strip()
    if not phone:
        print(f"  {R}[X]{RES} Phone number required.")
        return False
    try:
        client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        await client.start(phone)
        me = await client.get_me()
        print(f"  {G}[SUCCESS]{RES} Logged in as: {me.first_name}")
        await client.disconnect()
        return True
    except Exception as e:
        print(f"  {R}[ERROR]{RES} {e}")
        if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)
        return False

async def get_client():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start()
    return client

async def logout_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
        print(f"  {G}[OK]{RES} Session removed.")
    else:
        print(f"  {DIM}No session to remove.{RES}")

# ── PUBLIC MODE ──────────────────────────
def scrape_public(channel, limit=50, scrape_mode="all"):
    notify("PUBLIC", f"Scraping @{channel}", C)
    spinner("Connecting", 1.0)
    url=f"https://t.me/s/{channel}"
    configs=[]; offset=0
    while len(configs)<limit:
        try:
            r=requests.get(f"{url}?before={offset}" if offset else url,timeout=10)
            soup=BeautifulSoup(r.text,'html.parser')
            msgs=soup.find_all('div',class_='tgme_widget_message_text')
            if not msgs: break
            for msg in msgs:
                if len(configs)>=limit: break
                text=msg.get_text(separator='\n')
                found=extract(text,scrape_mode)
                for t,items in found.items():
                    for item in items:
                        if len(configs)>=limit: break
                        blessed=bless(t,item)
                        configs.append({"type":t,"config":item,"blessed":blessed,"channel":channel})
                        progress_bar(len(configs),limit)
                        st=f"{G}BLESSED{RES}" if blessed else f"{Y}RAW{RES}"
                        notify(t.upper(), item[:55], C)
            last=msgs[-1].parent.get('data-post','')
            offset=int(last.split('/')[-1]) if last else None
            if not offset: break
        except Exception as e:
            notify("ERROR", str(e), R); break
    notify("DONE", f"{len(configs)} configs extracted", G)
    return configs

# ── PRIVATE MODE ─────────────────────────
async def scrape_private(channel, limit=100, scrape_mode="all"):
    notify("PRIVATE", f"Scraping {channel}", C)
    spinner("Authenticating", 1.2)
    client = await get_client()
    configs=[]
    try:
        async for msg in client.iter_messages(channel, limit=limit):
            text=msg.text or ""
            txt_content = await download_txt(msg)
            if txt_content:
                text += "\n" + txt_content
                notify("TXT", "Deep file content extracted", G)
            if not text.strip(): continue
            found=extract(text,scrape_mode)
            for t,items in found.items():
                for item in items:
                    blessed=bless(t,item)
                    configs.append({"type":t,"config":item,"blessed":blessed,"channel":channel})
                    st=f"{G}BLESSED{RES}" if blessed else f"{Y}RAW{RES}"
                    notify(t.upper(), item[:55], C)
    except Exception as e:
        notify("ERROR", str(e), R)
    await client.disconnect()
    notify("DONE", f"{len(configs)} configs extracted", G)
    return configs

# ── LIVE MONITOR ─────────────────────────
async def live_monitor(channel):
    notify("LIVE", f"Watching {channel}", G)
    spinner("Starting live mode", 1.2)
    client = await get_client()
    @client.on(events.NewMessage(chats=channel))
    async def handler(event):
        text=event.message.text or ""
        txt_content = await download_txt(event.message, prefix="live")
        if txt_content: text += "\n" + txt_content
        if not text.strip(): return
        found=extract(text,"all")
        for t,items in found.items():
            for item in items:
                blessed=bless(t,item)
                st=f"{G}BLESSED{RES}" if blessed else f"{Y}RAW{RES}"
                notify(f"LIVE {t.upper()}", item[:55], G)
                save_configs([{"type":t,"config":item,"blessed":blessed,"channel":channel}])
    await client.run_until_disconnected()

# ── SCROLLABLE LOG VIEWER ─────────────────
def view_logs():
    f="blessed_configs.txt"
    if not os.path.exists(f):
        print(f"  {DIM}No saved configs yet.{RES}")
        input(f"\n  {DIM}[Enter]{RES}"); return
    with open(f) as fp: lines=[l.strip() for l in fp if l.strip()]
    if not lines:
        print(f"  {DIM}Log file empty.{RES}")
        input(f"\n  {DIM}[Enter]{RES}"); return
    page=0; per_page=8; total_pages=(len(lines)+per_page-1)//per_page
    while True:
        os.system('clear')
        print(f"  {C}{'═'*50}{RES}")
        print(f"  {G}SAVED LOGS{RES}  (Page {page+1}/{total_pages})  [N]ext [P]rev [Q]uit")
        print(f"  {C}{'═'*50}{RES}\n")
        start=page*per_page; end=start+per_page
        for i,line in enumerate(lines[start:end], start+1):
            print(f"  {DIM}[{i}]{RES} {line[:90]}")
        print()
        cmd=input(f"  {Y}[?]{RES} ").strip().lower()
        if cmd in ('n','next') and page<total_pages-1: page+=1
        elif cmd in ('p','prev') and page>0: page-=1
        elif cmd in ('q','quit'): break
        else: pass

def export_logs():
    f="blessed_configs.txt"
    if not os.path.exists(f):
        print(f"  {R}[!]{RES} No configs to export."); input(f"\n  {DIM}[Enter]{RES}"); return
    out=input(f"  {Y}[?]{RES} Export filename [export.json]: ").strip() or "export.json"
    configs=[]
    with open(f) as fp:
        lines=[l.strip() for l in fp if l.strip()]
    for i in range(0,len(lines),2):
        if i+1>=len(lines): break
        header=lines[i]; body=lines[i+1]
        parts=header.split()
        ctype=parts[0][1:-1] if parts else "unknown"
        status=parts[1] if len(parts)>1 else "RAW"
        configs.append({"type":ctype,"status":status,"config":body})
    with open(out,"w") as jf: json.dump(configs,jf,indent=2)
    print(f"  {G}[OK]{RES} Exported to {out}")
    input(f"\n  {DIM}[Enter]{RES}")

# ── SCRAPE METHOD MANAGER ────────────────
SCRAPE_METHODS = {"method":"all","description":"All config types"}

def manage_methods():
    global SCRAPE_METHODS
    while True:
        os.system('clear')
        print(f"  {C}{'═'*50}{RES}")
        print(f"  {G}SCRAPE METHOD MANAGER{RES}")
        print(f"  {C}{'═'*50}{RES}\n")
        print(f"  Current: {Y}{SCRAPE_METHODS['method']}{RES} - {DIM}{SCRAPE_METHODS['description']}{RES}\n")
        print(f"  {G}[1]{RES} All (configs + text + URLs)")
        print(f"  {G}[2]{RES} Configs only (vmess, vless, ssh, etc.)")
        print(f"  {G}[3]{RES} Text only (payloads, SNI, hosts)")
        print(f"  {G}[4]{RES} run.app URLs only")
        print(f"  {G}[5]{RES} TXT files only (deep extract)")
        print(f"  {G}[0]{RES} Back\n")
        ch=input(f"  {Y}[?]{RES} Choice: ").strip()
        if ch=='1': SCRAPE_METHODS={"method":"all","description":"All config types"}
        elif ch=='2': SCRAPE_METHODS={"method":"config","description":"Configs only"}
        elif ch=='3': SCRAPE_METHODS={"method":"text","description":"Text only"}
        elif ch=='4': SCRAPE_METHODS={"method":"runapp","description":"run.app URLs only"}
        elif ch=='5': SCRAPE_METHODS={"method":"txt","description":"TXT files only (deep extract)"}
        elif ch=='0': break
        print(f"  {G}[OK]{RES} Method updated.\n")

# ── MAIN MENU ──────────────────────────
def menu():
    print(f"  {G}[1]{RES} Scrape Telegram Channels")
    print(f"  {G}[2]{RES} View Saved Logs")
    print(f"  {G}[3]{RES} Export Saved Logs")
    print(f"  {G}[4]{RES} Change Scrape Method ({Y}{SCRAPE_METHODS['method']}{RES})")
    print(f"  {G}[5]{RES} Change Session Token (Logout/Login)")
    print(f"  {G}[0]{RES} Exit\n")
    return input(f"  {Y}[?]{RES} Choice: ").strip()

async def scrape_menu():
    os.system('clear')
    banner()
    print(f"  {G}[1]{RES} Public Channel")
    print(f"  {G}[2]{RES} Private Channel (Session)")
    print(f"  {G}[3]{RES} Live Monitor")
    print(f"  {G}[0]{RES} Back\n")
    ch=input(f"  {Y}[?]{RES} Choice: ").strip()
    if ch=='1':
        ch_name=input(f"  {Y}[?]{RES} Channel: ").replace("@","").replace("t.me/","")
        lim=int(input(f"  {Y}[?]{RES} Limit [50]: ") or "50")
        cfgs=scrape_public(ch_name,lim,SCRAPE_METHODS['method'])
        if cfgs: save_configs(cfgs)
    elif ch=='2':
        ch_name=input(f"  {Y}[?]{RES} Channel: ")
        lim=int(input(f"  {Y}[?]{RES} Limit [100]: ") or "100")
        cfgs=await scrape_private(ch_name,lim,SCRAPE_METHODS['method'])
        if cfgs: save_configs(cfgs)
    elif ch=='3':
        ch_name=input(f"  {Y}[?]{RES} Channel: ")
        await live_monitor(ch_name)
    input(f"\n  {DIM}[Enter]{RES}")

async def main():
    # Login once
    if not await detect_login():
        ok = await create_session()
        if not ok:
            print(f"  {R}[FATAL]{RES} Login required. Exiting.")
            sys.exit(1)
    else:
        client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        await client.start()
        me = await client.get_me()
        print(f"\n  {G}[WELCOME]{RES} {me.first_name} (@{me.username})\n")
        await client.disconnect()
        time.sleep(1.5)
    
    while True:
        banner()
        choice=menu()
        if choice=='0':
            pulse_glow(" GOODBYE! CONFIGS SAVED. ", 3, 0.3)
            break
        elif choice=='1': await scrape_menu()
        elif choice=='2': view_logs()
        elif choice=='3': export_logs()
        elif choice=='4': manage_methods()
        elif choice=='5':
            await logout_session()
            ok = await create_session()
            if not ok: print(f"  {R}[!]{RES} Login failed."); time.sleep(1)
        else:
            print(f"  {R}[!]{RES} Invalid choice"); time.sleep(0.5)

if __name__=="__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print(f"\n  {M}[STOPPED]{RES}\n"); sys.exit(0)
PYEOF
