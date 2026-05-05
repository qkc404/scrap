#!/usr/bin/env python3
# ============================================
# SCRAPER 2.0 TG — ULTIMATE VPN CONFIG TOOL
# Created by Saeka Tojirp
# Full TXT Extract | VPN Formats | Auto-Decrypt
# Live Messages | Session-Based | Full Control
# ============================================
import re, os, sys, asyncio, requests, time, shutil, subprocess, importlib, json

def auto_setup():
    packages = {"telethon":"telethon","requests":"requests","bs4":"beautifulsoup4"}
    for mod,pkg in packages.items():
        try: importlib.import_module(mod)
        except ImportError:
            print(f"\033[1;33m [*] Installing {pkg}...\033[0m")
            subprocess.run([sys.executable,"-m","pip","install",pkg],capture_output=True)
    bashrc=os.path.expanduser("~/.bashrc")
    alias_line="alias tgscrape='python3 ~/scraper.py'"
    if not os.path.exists(bashrc) or alias_line not in open(bashrc).read():
        os.system(f"echo \"{alias_line}\" >> {bashrc}")
auto_setup()
from bs4 import BeautifulSoup
from telethon import TelegramClient, events, functions
from telethon.tl.types import MessageMediaDocument

API_ID=2040
API_HASH="b18441a1ff607e10a989891a5462e627"
SESSION_FILE=os.path.expanduser("~/.prvtspy_session")
DECRYPT_BOT="@ScriptoolzDecrypt_bot"

R='\033[91m'; G='\033[92m'; Y='\033[93m'; B='\033[94m'
M='\033[95m'; C='\033[96m'; W='\033[97m'
BOLD='\033[1m'; DIM='\033[2m'; RES='\033[0m'

def tw(): return shutil.get_terminal_size().columns if hasattr(shutil,'get_terminal_size') else 60

def spinner(text="Loading",sec=1.2):
    frames=['◜','◠','◝','◞','◡','◟']; end=time.time()+sec; i=0
    while time.time()<end:
        sys.stdout.write(f"\r  {C}{frames[i%6]} {RES}{text}..."); sys.stdout.flush(); time.sleep(0.1); i+=1
    sys.stdout.write("\r"+" "*40+"\r")

def pulse_glow(text,times=3,delay=0.3):
    for _ in range(times):
        sys.stdout.write(f"\r  {G}{BOLD}{text}{RES}"); sys.stdout.flush(); time.sleep(delay/2)
        sys.stdout.write(f"\r  {DIM}{text}{RES}"); sys.stdout.flush(); time.sleep(delay/2)
    sys.stdout.write(f"\r  {G}{BOLD}{text}{RES}\n")

def notify(icon,msg,color=G): print(f"  [{color}{icon}{RES}] {msg}")

def banner(username=""):
    os.system('clear')
    w=tw()
    title="SCRAPER 2.0 TG"
    creator="Created by Saeka Tojirp"
    sys.stdout.write(f"{R}{BOLD}  {title}{RES}\n"); sys.stdout.flush(); time.sleep(0.04)
    sys.stdout.write(f"{B}{BOLD}  {title}{RES}\n"); sys.stdout.flush(); time.sleep(0.04)
    sys.stdout.write(f"{G}{BOLD}  {title}{RES}\n"); sys.stdout.flush(); time.sleep(0.02)
    if username: print(f"{C}  Hi! {username}{RES}")
    print(f"{DIM}  {creator}{RES}")
    print(f"{C}  {'─'*w}{RES}\n")

# ── VPN FILE EXTENSIONS ──────────────────
VPN_EXTENSIONS = (
    '.ehi','.ehil','.hc','.npvt','.npvtsub','.dark','.v2','.sip','.hat',
    '.nm','.tnl','.slipnet','.tls','.lnk','.mina','.ssc',
    '.aura','.bcl','.bee','.btv','.ena','.vel','.eta','.fix','.glory',
    '.marvs','.nur','.md','.mdvpn','.ost','.osv','.ry','.t20','.tik',
    '.tsm','.tx','.ulti','.ultra','.vlx','.wolf','.mmt',
    '.tcx','.7net','.ihome','.xhypher','.izph','.osp','.bshield','.enz',
    '.maya','.roy','.ar',
    '.apnalite','.bdnet','.hxt','.4ulite','.fnf','.omanova','.ursa','.hsome',
    '.stk','.ziv','.wyr','.int','.eut'
)

VPN_PREFIXES = (
    'darktunnel://','nm-','slipnet-enc://','slipnet://','ssc://',
    'aura://','bcl://','bee://','btv://','ena://','vel://','eta://',
    'fix://','glory://','marvs://','nur://','mdvpn://','md://','ost://',
    'osv://','ry://','t20://','tik://','tsm://','tx://','ulti://',
    'ultra://','vlx://','wolf://','mmt://',
    'tcx://','tcxtunnelplus://','tunnelcoreplus://','7net://','7netvpn://',
    'ihome://','ihomevpn://','xhypher://','xhyphertunnelpro://',
    'izph://','izphvpnpro://','osp://','osptunnel://','bshield://','bshieldnet://',
    'enz://','enztunnellite://',
    'apnalite://','bdnet://','hxt://','4ulite://','fnf://','omanova://',
    'ursa://','hsome://','zivpn://','wyrvpn://','intvpn://','eut-settings://'
)

PATTERNS={
    "ssh":r"ssh://[^\s]+","vmess":r"vmess://[^\s]+","vless":r"vless://[^\s]+",
    "trojan":r"trojan://[^\s]+","ssr":r"ssr://[^\s]+","ss":r"ss://[^\s]+",
    "hysteria":r"hysteria://[^\s]+","tuic":r"tuic://[^\s]+",
    "http_custom":r"Host:\s*[^\s]+.*(?:Upgrade|Connection|User-Agent).*",
    "payload":r"(?:GET|POST|CONNECT|PUT|HEAD)\s+[^\s]+\s+HTTP/\d\.\d.*",
    "sni":r"(?:SNI|sni|bug)\s*[:=]\s*[^\s]+",
    "ip_port":r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+",
}

def extract_full_text(text):
    results=[]
    for line in text.split('\n'):
        line=line.strip()
        if not line or len(line)<5: continue
        if line.startswith(('─','═','━','-','•')): continue
        if line in ('.','..','...'): continue
        results.append(line)
    return results

def extract_patterns(text):
    found={}
    for n,p in PATTERNS.items():
        m=re.findall(p,text,re.I)
        if m: found[n]=list(set(m))
    return found

def detect_vpn_file(filename):
    """Check if file is a VPN config file."""
    if not filename: return False
    fn=filename.lower()
    for ext in VPN_EXTENSIONS:
        if fn.endswith(ext): return True
    return False

def detect_vpn_prefix(text):
    """Check if text contains VPN config prefixes."""
    for prefix in VPN_PREFIXES:
        if prefix.lower() in text.lower(): return True
    return False

def bless(t,c):
    if t in ["vmess","vless","trojan","ssh","ss","ssr","hysteria","tuic"]:
        return c.startswith(f"{t}://")
    return True

def save_configs(configs,filename="blessed_configs.txt"):
    with open(filename,"a",encoding="utf-8") as f:
        for c in configs:
            status="BLESSED" if c['blessed'] else "RAW"
            f.write(f"[{c['type'].upper()}] [{status}] {c['channel']}\n{c['config']}\n{'-'*40}\n")

def save_decrypted(configs,filename="decrypted_configs.txt"):
    with open(filename,"a",encoding="utf-8") as f:
        for c in configs:
            f.write(f"[DECRYPTED] [{c['type']}] {c['channel']}\n{c['config']}\n{'-'*40}\n")

def save_vpn_protocols(configs,filename="vpn_protocols.txt"):
    with open(filename,"a",encoding="utf-8") as f:
        for c in configs:
            f.write(f"[{c['type'].upper()}] {c['channel']}\n{c['config']}\n{'-'*40}\n")

# ── TXT FULL CONTENT EXTRACTOR ──────────
async def download_file_full(message, prefix="dl"):
    if not message.media: return None,None
    doc=getattr(message.media,'document',None)
    if not doc: return None,None
    fname=None
    for a in doc.attributes:
        if hasattr(a,'file_name') and a.file_name: fname=a.file_name; break
    if not fname: fname=f"{prefix}_file"
    try:
        fpath=f"_{prefix}_{fname}"
        await message.download_media(file=fpath)
        with open(fpath,"r",encoding="utf-8",errors="ignore") as f:
            content=f.read()
        os.remove(fpath)
        return fname,content
    except: return fname,""

# ── DECRYPT VIA BOT ──────────────────────
async def decrypt_via_bot(client, message):
    """Forward VPN file to decrypt bot and wait for decrypted response."""
    try:
        notify("DECRYPT","Forwarding to decrypt bot...",Y)
        # Forward to bot
        await client.forward_messages(DECRYPT_BOT,message)
        # Wait for bot response (max 30 sec)
        async for response in client.iter_messages(DECRYPT_BOT,limit=5,timeout=30):
            if response.media and hasattr(response.media,'document'):
                fname,content=await download_file_full(response,"decrypted")
                if content:
                    notify("DECRYPT",f"Decrypted: {fname}",G)
                    return content
            # Check if response has text with config
            if response.text and len(response.text)>20:
                notify("DECRYPT","Text response received",G)
                return response.text
        notify("DECRYPT","No response from bot",Y)
        return None
    except Exception as e:
        notify("DECRYPT ERROR",str(e),R)
        return None

# ── SESSION MANAGER ──────────────────────
async def detect_login():
    if not os.path.exists(SESSION_FILE): return False
    try:
        client=TelegramClient(SESSION_FILE,API_ID,API_HASH)
        await client.start()
        await client.disconnect()
        return True
    except: return False

async def create_session():
    if await detect_login():
        client=TelegramClient(SESSION_FILE,API_ID,API_HASH)
        await client.start()
        me=await client.get_me()
        print(f"\n  {G}[WELCOME]{RES} {me.first_name} (@{me.username})")
        await client.disconnect()
        return True,me
    print(f"\n  {Y}[!]{RES} No session found. One-time login required.")
    phone=input(f"  {Y}[?]{RES} Phone number (+63...): ").strip()
    if not phone: return False,None
    try:
        client=TelegramClient(SESSION_FILE,API_ID,API_HASH)
        await client.start(phone)
        me=await client.get_me()
        print(f"  {G}[SUCCESS]{RES} Logged in as: {me.first_name}")
        await client.disconnect()
        return True,me
    except Exception as e:
        print(f"  {R}[ERROR]{RES} {e}")
        if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)
        return False,None

async def get_client():
    client=TelegramClient(SESSION_FILE,API_ID,API_HASH)
    await client.start()
    return client

async def logout_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
        print(f"  {G}[OK]{RES} Session removed.")
    else: print(f"  {DIM}No session to remove.{RES}")

# ── LIVE MESSAGE VIEWER ─────────────────
async def live_message_viewer(channel):
    client=await get_client()
    notify("LIVE MSG",f"Viewing {channel} - New messages appear below",G)
    print(f"  {DIM}[CTRL+C to exit]{RES}\n")
    @client.on(events.NewMessage(chats=channel))
    async def handler(event):
        text=event.message.text or ""
        if event.message.media:
            doc=getattr(event.message.media,'document',None)
            if doc:
                fname=""
                for a in doc.attributes:
                    if hasattr(a,'file_name'): fname=a.file_name; break
                print(f"\n  {C}[FILE]{RES} {fname} ({doc.size} bytes)")
        if text:
            for line in text.split('\n'):
                if line.strip():
                    print(f"  {DIM}{line[:100]}{RES}")
        print(f"  {C}{'─'*40}{RES}")
    await client.run_until_disconnected()

# ── CHANNEL SCRAPER (PUBLIC) ────────────
def scrape_public(channel,limit=50):
    notify("PUBLIC",f"Scraping @{channel}",C)
    spinner("Connecting",1.0)
    url=f"https://t.me/s/{channel}"; configs=[]; offset=0
    while len(configs)<limit:
        try:
            r=requests.get(f"{url}?before={offset}" if offset else url,timeout=10)
            soup=BeautifulSoup(r.text,'html.parser')
            msgs=soup.find_all('div',class_='tgme_widget_message_text')
            if not msgs: break
            for msg in msgs:
                if len(configs)>=limit: break
                text=msg.get_text(separator='\n')
                # Full text extract
                lines=extract_full_text(text)
                for line in lines:
                    if len(configs)>=limit: break
                    if detect_vpn_prefix(line):
                        configs.append({"type":"VPN_PREFIX","config":line,"blessed":True,"channel":channel})
                        notify("VPN",line[:55],M)
                    else:
                        found=extract_patterns(line)
                        for t,items in found.items():
                            for item in items:
                                if len(configs)>=limit: break
                                blessed=bless(t,item)
                                configs.append({"type":t,"config":item,"blessed":blessed,"channel":channel})
                                st=f"{G}BLESSED{RES}" if blessed else f"{Y}RAW{RES}"
                                notify(t.upper(),item[:55],C)
            last=msgs[-1].parent.get('data-post','')
            offset=int(last.split('/')[-1]) if last else None
            if not offset: break
        except Exception as e:
            notify("ERROR",str(e),R); break
    notify("DONE",f"{len(configs)} configs",G)
    return configs

# ── CHANNEL SCRAPER (PRIVATE) ───────────
async def scrape_private(client,channel,limit=100):
    notify("PRIVATE",f"Scraping {channel}",C)
    spinner("Authenticating",1.0)
    configs=[]; decrypted_configs=[]
    try:
        async for msg in client.iter_messages(channel,limit=limit):
            text=msg.text or ""
            # Process .txt files
            if msg.media:
                doc=getattr(msg.media,'document',None)
                if doc:
                    fname=""
                    for a in doc.attributes:
                        if hasattr(a,'file_name'): fname=a.file_name; break
                    # Check if VPN config file
                    if detect_vpn_file(fname):
                        notify("VPN FILE",fname,M)
                        # Decrypt via bot
                        decrypted=await decrypt_via_bot(client,msg)
                        if decrypted:
                            decrypted_configs.append({"type":"DECRYPTED","config":decrypted,"channel":channel})
                            save_decrypted([{"type":"DECRYPTED","config":decrypted,"channel":channel,"blessed":True}])
                            # Also extract from decrypted content
                            for line in decrypted.split('\n'):
                                line=line.strip()
                                if not line or len(line)<5: continue
                                if detect_vpn_prefix(line):
                                    configs.append({"type":"VPN","config":line,"blessed":True,"channel":channel})
                                    notify("VPN",line[:55],M)
                                found=extract_patterns(line)
                                for t,items in found.items():
                                    for item in items:
                                        configs.append({"type":t,"config":item,"blessed":bless(t,item),"channel":channel})
                        continue
                    # Regular .txt file
                    if doc.mime_type=="text/plain" or fname.endswith(('.txt','.log','.cfg','.conf','.json')):
                        _,content=await download_file_full(msg)
                        if content:
                            text+="\n"+content
                            notify("TXT",f"Extracted {len(content)} chars from {fname}",G)
            if not text.strip(): continue
            # Extract every line
            lines=extract_full_text(text)
            for line in lines:
                if detect_vpn_prefix(line):
                    configs.append({"type":"VPN_PREFIX","config":line,"blessed":True,"channel":channel})
                    notify("VPN",line[:55],M)
                found=extract_patterns(line)
                for t,items in found.items():
                    for item in items:
                        configs.append({"type":t,"config":item,"blessed":bless(t,item),"channel":channel})
    except Exception as e:
        notify("ERROR",str(e),R)
    save_configs(configs)
    if decrypted_configs: save_vpn_protocols(decrypted_configs)
    notify("DONE",f"{len(configs)} configs + {len(decrypted_configs)} decrypted",G)
    return configs,decrypted_configs

# ── LIVE MONITOR ────────────────────────
async def live_monitor(channel):
    client=await get_client()
    notify("LIVE",f"Watching {channel}",G)
    @client.on(events.NewMessage(chats=channel))
    async def handler(event):
        text=event.message.text or ""
        if event.message.media:
            doc=getattr(event.message.media,'document',None)
            if doc:
                fname=""
                for a in doc.attributes:
                    if hasattr(a,'file_name'): fname=a.file_name; break
                if detect_vpn_file(fname):
                    _,content=await download_file_full(event.message)
                    if content:
                        text+="\n"+content
                        notify("VPN FILE",fname,M)
        if not text.strip(): return
        for line in extract_full_text(text):
            if detect_vpn_prefix(line):
                notify("LIVE VPN",line[:55],M)
                save_vpn_protocols([{"type":"VPN","config":line,"channel":channel,"blessed":True}])
            found=extract_patterns(line)
            for t,items in found.items():
                for item in items:
                    notify(f"LIVE {t.upper()}",item[:55],G)
                    save_configs([{"type":t,"config":item,"blessed":bless(t,item),"channel":channel}])
    await client.run_until_disconnected()

# ── SAVED LOG VIEWERS ──────────────────
def view_saved(filename,title):
    if not os.path.exists(filename):
        print(f"  {DIM}No data in {filename}{RES}")
        input(f"\n  {DIM}[Enter]{RES}"); return
    with open(filename) as f: lines=[l.strip() for l in f if l.strip()]
    if not lines:
        print(f"  {DIM}File empty.{RES}")
        input(f"\n  {DIM}[Enter]{RES}"); return
    page=0; per_page=10; total=(len(lines)+per_page-1)//per_page
    while True:
        os.system('clear')
        print(f"  {C}{'═'*50}{RES}")
        print(f"  {G}{title}{RES}  Page {page+1}/{total}  [N]ext [P]rev [Q]uit")
        print(f"  {C}{'═'*50}{RES}\n")
        for i,line in enumerate(lines[page*per_page:(page+1)*per_page],page*per_page+1):
            print(f"  {DIM}[{i}]{RES} {line[:90]}")
        cmd=input(f"\n  {Y}[?]{RES} ").strip().lower()
        if cmd in ('n','next') and page<total-1: page+=1
        elif cmd in ('p','prev') and page>0: page-=1
        elif cmd in ('q','quit'): break

def export_logs(filename,title):
    if not os.path.exists(filename):
        print(f"  {R}[!]{RES} No data."); input(f"\n  {DIM}[Enter]{RES}"); return
    out=input(f"  {Y}[?]{RES} Export as [export.json]: ").strip() or "export.json"
    configs=[]
    with open(filename) as f:
        for line in f:
            line=line.strip()
            if line.startswith('[') and ']' in line:
                configs.append({"raw":line})
    with open(out,"w") as jf: json.dump(configs,jf,indent=2)
    print(f"  {G}[OK]{RES} Exported to {out}")
    input(f"\n  {DIM}[Enter]{RES}")

# ── MENUS ──────────────────────────────
def main_menu():
    print(f"  {G}[1]{RES} Scrape Telegram Channels")
    print(f"  {G}[2]{RES} View Saved Logs")
    print(f"  {G}[3]{RES} Export Saved Logs")
    print(f"  {G}[4]{RES} Live Message Viewer")
    print(f"  {G}[5]{RES} Change Session (Logout/Login)")
    print(f"  {G}[0]{RES} Exit\n")
    return input(f"  {Y}[?]{RES} Choice: ").strip()

def logs_menu():
    os.system('clear')
    banner(current_user)
    print(f"  {G}[1]{RES} View All Blessed Configs")
    print(f"  {G}[2]{RES} View Decrypted Configs")
    print(f"  {G}[3]{RES} View VPN Protocols")
    print(f"  {G}[0]{RES} Back\n")
    ch=input(f"  {Y}[?]{RES} Choice: ").strip()
    if ch=='1': view_saved("blessed_configs.txt","ALL BLESSED CONFIGS")
    elif ch=='2': view_saved("decrypted_configs.txt","DECRYPTED CONFIGS")
    elif ch=='3': view_saved("vpn_protocols.txt","VPN PROTOCOLS")

def export_menu():
    os.system('clear')
    banner(current_user)
    print(f"  {G}[1]{RES} Export Blessed Configs")
    print(f"  {G}[2]{RES} Export Decrypted Configs")
    print(f"  {G}[3]{RES} Export VPN Protocols")
    print(f"  {G}[0]{RES} Back\n")
    ch=input(f"  {Y}[?]{RES} Choice: ").strip()
    if ch=='1': export_logs("blessed_configs.txt","BLESSED CONFIGS")
    elif ch=='2': export_logs("decrypted_configs.txt","DECRYPTED CONFIGS")
    elif ch=='3': export_logs("vpn_protocols.txt","VPN PROTOCOLS")

async def scrape_me
