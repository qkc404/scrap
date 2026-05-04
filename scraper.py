#!/usr/bin/env python3
# ============================================
# SCRAPER 2.0 TG — SESSION-BASED (NO API INPUT)
# Auto-Login via Pre-Built Session | Glitch+Glow
# Public | Private+TXT | Live Monitor | All FX
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

# ── BUILT-IN API (NO USER INPUT) ─────────
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
SESSION_FILE = os.path.expanduser("~/.prvtspy_session")

# ── COLORS ────────────────────────────────
R='\033[91m'; G='\033[92m'; Y='\033[93m'; B='\033[94m'
M='\033[95m'; C='\033[96m'; W='\033[97m'
BOLD='\033[1m'; DIM='\033[2m'; RES='\033[0m'
BG_G='\033[42m'; BG_R='\033[41m'; BG_C='\033[46m'

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
    sys.stdout.write("\r"+" "*30+"\r")

def progress_bar(current, total, label="Scraping"):
    pct = (current*100)//total if total else 100
    bar_len = 40
    filled = (current*bar_len)//total if total else bar_len
    bar = f"{G}{'█'*filled}{DIM}{'░'*(bar_len-filled)}{RES}"
    sys.stdout.write(f"\r  {label}: |{bar}| {pct}%")
    sys.stdout.flush()
    if current == total: sys.stdout.write("\n")

def type_text(text, color=W, speed=0.02):
    for c in text:
        sys.stdout.write(f"{color}{c}{RES}")
        sys.stdout.flush()
        time.sleep(speed)
    print()

def pulse_glow(text, times=3, delay=0.3):
    for _ in range(times):
        sys.stdout.write(f"\r  {G}{BOLD}{text}{RES}")
        sys.stdout.flush(); time.sleep(delay/2)
        sys.stdout.write(f"\r  {DIM}{text}{RES}")
        sys.stdout.flush(); time.sleep(delay/2)
    sys.stdout.write(f"\r  {G}{BOLD}{text}{RES}\n")

# ── GLITCH + GLOW BANNER ─────────────────
def banner():
    os.system('clear')
    w = term_width()
    title = "SCRAPER 2.0 TG"
    line = "═" * w
    sub = "[ PUBLIC • PRIVATE • LIVE • TXT • SESSION‑BASED ]"
    # Glitch red
    sys.stdout.write(f"{R}{BOLD}  {title}  {RES}\n"); sys.stdout.flush(); time.sleep(0.05)
    # Glitch blue
    sys.stdout.write(f"{B}{BOLD}  {title}  {RES}\n"); sys.stdout.flush(); time.sleep(0.05)
    # Glow green
    sys.stdout.write(f"{G}{BOLD}  {title}  {RES}\n"); sys.stdout.flush(); time.sleep(0.02)
    print(f"{DIM}  {sub}{RES}")
    print(f"{C}  {line}{RES}")
    print()

# ── PATTERNS ─────────────────────────────
PATTERNS={
    "ssh":r"ssh://[^\s]+","vmess":r"vmess://[^\s]+","vless":r"vless://[^\s]+",
    "trojan":r"trojan://[^\s]+","ssr":r"ssr://[^\s]+","ss":r"ss://[^\s]+",
    "hysteria":r"hysteria://[^\s]+","tuic":r"tuic://[^\s]+",
    "http":r"(?:server|proxy|host)\s*[:=]\s*[^\s]+",
    "payload":r"(?:GET|POST|CONNECT|PUT|HEAD)\s+[^\s]+\s+HTTP/\d\.\d",
    "sni":r"(?:SNI|sni|bug)\s*[:=]\s*[^\s]+",
}

def extract(text):
    found={}
    for n,p in PATTERNS.items():
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

# ── TXT DOWNLOADER ───────────────────────
async def download_txt(message, prefix="temp"):
    if not message.media: return ""
    doc = getattr(message.media, 'document', None)
    if not doc: return ""
    is_txt = doc.mime_type == "text/plain" or any(
        getattr(a, 'file_name', '').endswith('.txt')
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

# ── SESSION CREATOR (FIRST-TIME) ──────────
async def create_session():
    """Create session if it does not exist (first run)"""
    if os.path.exists(SESSION_FILE):
        return True
    print(f"\n  {Y}[!]{RES} No session found. Creating new session...")
    phone = input(f"  {Y}[?]{RES} Phone number (+63...): ").strip()
    if not phone:
        print(f"  {R}[X]{RES} Phone number required for first-time setup.")
        return False
    try:
        client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        await client.start(phone)
        me = await client.get_me()
        print(f"  {G}[OK]{RES} Session created! Logged in as: {me.first_name}")
        await client.disconnect()
        return True
    except Exception as e:
        print(f"  {R}[ERROR]{RES} {e}")
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        return False

async def get_client():
    """Return authenticated client. Creates session if missing."""
    if not os.path.exists(SESSION_FILE):
        ok = await create_session()
        if not ok:
            sys.exit(1)
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start()
    return client

# ── PUBLIC MODE ──────────────────────────
def scrape_public(channel, limit=50):
    print(f"  {C}[*]{RES} Public scraping: @{channel}")
    spinner("Connecting to public feed", 1.2)
    url=f"https://t.me/s/{channel}"
    configs=[]; offset=0; total_found=0
    while len(configs)<limit:
        try:
            r=requests.get(f"{url}?before={offset}" if offset else url,timeout=10)
            soup=BeautifulSoup(r.text,'html.parser')
            msgs=soup.find_all('div',class_='tgme_widget_message_text')
            if not msgs: break
            for idx,msg in enumerate(msgs):
                if len(configs)>=limit: break
                text=msg.get_text(separator='\n')
                found=extract(text)
                for t,items in found.items():
                    for item in items:
                        if len(configs)>=limit: break
                        blessed=bless(t,item)
                        configs.append({"type":t,"config":item,"blessed":blessed,"channel":channel})
                        total_found+=1
                        progress_bar(len(configs),limit)
                        st=f"{G}BLESSED{RES}" if blessed else f"{Y}RAW{RES}"
                        print(f"\n  [{C}{t.upper():10}{RES}] [{st}] {item[:60]}...")
            last=msgs[-1].parent.get('data-post','')
            offset=int(last.split('/')[-1]) if last else None
            if not offset: break
        except Exception as e:
            print(f"\n  {R}[!]{RES} {e}"); break
    print(f"\n  {G}[DONE]{RES} {len(configs)} configs extracted\n")
    return configs

# ── PRIVATE MODE (SESSION-BASED + TXT) ──
async def scrape_private(channel, limit=100):
    print(f"  {C}[*]{RES} Private scraping: {channel}")
    spinner("Authenticating with saved session", 1.5)
    client = await get_client()
    configs=[]
    try:
        msg_count=0
        async for msg in client.iter_messages(channel, limit=limit):
            msg_count+=1
            text=msg.text or ""
            # Download and parse .txt attachments
            txt_content = await download_txt(msg)
            if txt_content:
                text += "\n" + txt_content
                print(f"  {G}[TXT]{RES} Extracted text from attached file")
            if not text.strip(): continue
            found=extract(text)
            for t,items in found.items():
                for item in items:
                    blessed=bless(t,item)
                    configs.append({"type":t,"config":item,"blessed":blessed,"channel":channel})
                    st=f"{G}BLESSED{RES}" if blessed else f"{Y}RAW{RES}"
                    print(f"  [{C}{t.upper():10}{RES}] [{st}] {item[:60]}...")
        print(f"  {DIM}Scanned {msg_count} messages.{RES}")
    except Exception as e:
        print(f"  {R}[!]{RES} {e}")
    await client.disconnect()
    print(f"\n  {G}[DONE]{RES} {len(configs)} configs extracted\n")
    return configs

# ── LIVE MONITOR ─────────────────────────
async def live_monitor(channel):
    print(f"  {C}[*]{RES} Live monitor: {channel}")
    spinner("Starting live mode", 1.5)
    client = await get_client()
    print(f"  {G}[LIVE]{RES} Watching for new messages... (CTRL+C to stop)\n")
    @client.on(events.NewMessage(chats=channel))
    async def handler(event):
        text=event.message.text or ""
        txt_content = await download_txt(event.message, prefix="live")
        if txt_content:
            text += "\n" + txt_content
            print(f"  {G}[TXT]{RES} Live attachment extracted")
        if not text.strip(): return
        found=extract(text)
        for t,items in found.items():
            for item in items:
                blessed=bless(t,item)
                st=f"{G}BLESSED{RES}" if blessed else f"{Y}RAW{RES}"
                print(f"  [{G}LIVE{RES}] [{C}{t.upper():10}{RES}] [{st}] {item[:60]}...")
                save_configs([{"type":t,"config":item,"blessed":blessed,"channel":channel}])
    await client.run_until_disconnected()

# ── MENU ─────────────────────────────────
def menu():
    print(f"  {G}[1]{RES} Public Channel Scraper")
    print(f"  {G}[2]{RES} Private Channel Scraper (Session + TXT)")
    print(f"  {G}[3]{RES} Live Monitor (Real‑Time + TXT)")
    print(f"  {G}[4]{RES} View Saved Configs")
    print(f"  {G}[5]{RES} Export Saved Configs to JSON")
    print(f"  {G}[6]{RES} Change Session (Re‑login)")
    print(f"  {G}[0]{RES} Exit\n")
    return input(f"  {Y}[?]{RES} Choice: ").strip()

def view_saved():
    f="blessed_configs.txt"
    if os.path.exists(f):
        with open(f) as fp: lines=fp.readlines()
        count=sum(1 for l in lines if l.startswith('['))
        print(f"  {G}[+]{RES} {count} configs saved\n")
        for l in lines[-25:]: print(f"  {DIM}{l.rstrip()[:100]}{RES}")
    else: print(f"  {DIM}No saved configs yet.{RES}")
    input(f"\n  {DIM}[Enter]{RES}")

def export_json():
    f="blessed_configs.txt"
    if not os.path.exists(f):
        print(f"  {R}[!]{RES} No configs to export.")
        input(f"\n  {DIM}[Enter]{RES}"); return
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
    with open("export.json","w") as jf: json.dump(configs,jf,indent=2)
    print(f"  {G}[OK]{RES} Exported to export.json")
    input(f"\n  {DIM}[Enter]{RES}")

async def change_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
        print(f"  {G}[OK]{RES} Old session removed.")
    await create_session()
    input(f"\n  {DIM}[Enter]{RES}")

async def main():
    # Ensure session exists on first run
    if not os.path.exists(SESSION_FILE):
        await create_session()
    while True:
        banner()
        choice=menu()
        if choice=="0":
            pulse_glow(" GOODBYE! CONFIGS SAVED. ", 3, 0.3)
            break
        elif choice=="1":
            ch=input(f"  {Y}[?]{RES} Channel: ").replace("@","").replace("t.me/","")
            lim=int(input(f"  {Y}[?]{RES} Limit [50]: ") or "50")
            cfgs=scrape_public(ch,lim)
            if cfgs: save_configs(cfgs)
            input(f"\n  {DIM}[Enter]{RES}")
        elif choice=="2":
            ch=input(f"  {Y}[?]{RES} Channel: ")
            lim=int(input(f"  {Y}[?]{RES} Limit [100]: ") or "100")
            cfgs=await scrape_private(ch,lim)
            if cfgs: save_configs(cfgs)
            input(f"\n  {DIM}[Enter]{RES}")
        elif choice=="3":
            ch=input(f"  {Y}[?]{RES} Channel: ")
            await live_monitor(ch)
        elif choice=="4":
            view_saved()
        elif choice=="5":
            export_json()
        elif choice=="6":
            await change_session()
        else:
            print(f"  {R}[!]{RES} Invalid choice"); time.sleep(1)

if __name__=="__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print(f"\n  {M}[STOPPED]{RES}\n"); sys.exit(0)
PYEOF
