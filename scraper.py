pkg update -y && pkg upgrade -y && pkg install python python-pip wget curl -y && pip install telethon requests beautifulsoup4 -q && cat > scraper.py << 'PYEOF'
#!/usr/bin/env python3
# ============================================
# SCRAPER 2.0 TG — BOT MODE (NO ACCOUNT)
# Created by Saeka Tojirp
# Bot Token Auth | No Number | No Freeze
# Full Scraper | Auto-Decrypt | Live Monitor
# ============================================
import re, os, sys, asyncio, requests, time, shutil, subprocess, importlib, json
from datetime import datetime
from pathlib import Path

def auto_setup():
    packages = {"telethon":"telethon","requests":"requests","bs4":"beautifulsoup4"}
    for mod,pkg in packages.items():
        try: importlib.import_module(mod)
        except ImportError:
            print(f"\033[1;33m  [*] Installing {pkg}...\033[0m")
            subprocess.run([sys.executable,"-m","pip","install",pkg],capture_output=True)
    bashrc=os.path.expanduser("~/.bashrc")
    alias_line="alias tgscrape='python3 ~/scraper.py'"
    if not os.path.exists(bashrc) or alias_line not in open(bashrc).read():
        os.system(f"echo \"{alias_line}\" >> {bashrc}")
auto_setup()
from bs4 import BeautifulSoup
from telethon import TelegramClient, events, functions, types
from telethon.tl.types import MessageMediaDocument
from telethon.errors import FloodWaitError

API_ID=2040
API_HASH="b18441a1ff607e10a989891a5462e627"
SESSION_FILE=os.path.expanduser("~/.prvtspy_bot_session")
TOKEN_FILE=os.path.expanduser("~/.prvtspy_bot_token")
DECRYPT_BOT="@ScriptoolzDecrypt_bot"
RECENT_FILE=os.path.expanduser("~/.prvtspy_recent.json")

R='\033[91m'; G='\033[92m'; Y='\033[93m'; B='\033[94m'
M='\033[95m'; C='\033[96m'; W='\033[97m'
BOLD='\033[1m'; DIM='\033[2m'; RES='\033[0m'
BG_G='\033[42m'; BG_R='\033[41m'; BG_C='\033[46m'; BG_M='\033[45m'

def tw(): return shutil.get_terminal_size().columns if hasattr(shutil,'get_terminal_size') else 60
def spinner(text="Processing", sec=1.2):
    frames=['◜','◠','◝','◞','◡','◟']
    end=time.time()+sec; i=0
    while time.time()<end:
        sys.stdout.write(f"\r  {C}{frames[i%6]} {RES}{text}...")
        sys.stdout.flush(); time.sleep(0.08); i+=1
    sys.stdout.write("\r"+" "*50+"\r")

def pulse_glow(text, times=3, delay=0.3):
    for _ in range(times):
        sys.stdout.write(f"\r  {G}{BOLD}{text}{RES}"); sys.stdout.flush(); time.sleep(delay/2)
        sys.stdout.write(f"\r  {DIM}{text}{RES}"); sys.stdout.flush(); time.sleep(delay/2)
    sys.stdout.write(f"\r  {G}{BOLD}{text}{RES}\n")

def notify(icon, msg, color=G):
    ts=datetime.now().strftime("%H:%M:%S")
    print(f"  [{DIM}{ts}{RES}] [{color}{icon}{RES}] {msg}")

def banner(username=""):
    os.system('clear')
    title="SCRAPER 2.0 TG"
    creator="Created by Saeka Tojirp"
    sys.stdout.write(f"\n{R}{BOLD}  {title}{RES}\n"); sys.stdout.flush(); time.sleep(0.03)
    sys.stdout.write(f"{B}{BOLD}  {title}{RES}\n"); sys.stdout.flush(); time.sleep(0.03)
    sys.stdout.write(f"{G}{BOLD}  {title}{RES}\n"); sys.stdout.flush(); time.sleep(0.02)
    if username: print(f"{C}  Hi! {username}{RES}")
    print(f"{DIM}  {creator}{RES}")
    print(f"{C}  {'─'*tw()}{RES}")

# ── VPN DETECTION ──────────────────────
VPN_EXTENSIONS = ('.ehi','.ehil','.hc','.npvt','.npvtsub','.dark','.v2','.sip','.hat','.nm','.tnl','.slipnet','.tls','.lnk','.mina','.ssc','.aura','.bcl','.bee','.btv','.ena','.vel','.eta','.fix','.glory','.marvs','.nur','.md','.mdvpn','.ost','.osv','.ry','.t20','.tik','.tsm','.tx','.ulti','.ultra','.vlx','.wolf','.mmt','.tcx','.7net','.ihome','.xhypher','.izph','.osp','.bshield','.enz','.maya','.roy','.ar','.apnalite','.bdnet','.hxt','.4ulite','.fnf','.omanova','.ursa','.hsome','.stk','.ziv','.wyr','.int','.eut')
VPN_PREFIXES = ('darktunnel://','nm-','slipnet-enc://','slipnet://','ssc://','aura://','bcl://','bee://','btv://','ena://','vel://','eta://','fix://','glory://','marvs://','nur://','mdvpn://','md://','ost://','osv://','ry://','t20://','tik://','tsm://','tx://','ulti://','ultra://','vlx://','wolf://','mmt://','tcx://','tcxtunnelplus://','tunnelcoreplus://','7net://','7netvpn://','ihome://','ihomevpn://','xhypher://','xhyphertunnelpro://','izph://','izphvpnpro://','osp://','osptunnel://','bshield://','bshieldnet://','enz://','enztunnellite://','apnalite://','bdnet://','hxt://','4ulite://','fnf://','omanova://','ursa://','hsome://','zivpn://','wyrvpn://','intvpn://','eut-settings://')
PATTERNS={"ssh":r"ssh://[^\s]+","vmess":r"vmess://[^\s]+","vless":r"vless://[^\s]+","trojan":r"trojan://[^\s]+","ssr":r"ssr://[^\s]+","ss":r"ss://[^\s]+","hysteria":r"hysteria://[^\s]+","tuic":r"tuic://[^\s]+","http_custom":r"Host:\s*[^\s]+.*(?:Upgrade|Connection|User-Agent).*","payload":r"(?:GET|POST|CONNECT|PUT|HEAD)\s+[^\s]+\s+HTTP/\d\.\d.*","sni":r"(?:SNI|sni|bug)\s*[:=]\s*[^\s]+","ip_port":r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"}

RECENT_CHANNELS=[]
def load_recent():
    global RECENT_CHANNELS
    if os.path.exists(RECENT_FILE):
        try:
            with open(RECENT_FILE) as f: RECENT_CHANNELS=json.load(f)
        except: RECENT_CHANNELS=[]

def save_recent(channel):
    global RECENT_CHANNELS
    if channel not in RECENT_CHANNELS:
        RECENT_CHANNELS.insert(0,channel)
        RECENT_CHANNELS=RECENT_CHANNELS[:10]
        with open(RECENT_FILE,"w") as f: json.dump(RECENT_CHANNELS,f)

def extract_full_text(text):
    r=[]
    for line in text.split('\n'):
        line=line.strip()
        if not line or len(line)<5: continue
        if line.startswith(('─','═','━','-','•','#')): continue
        if line in ('.','..','...','⋯'): continue
        r.append(line)
    return r

def extract_patterns(text):
    found={}
    for n,p in PATTERNS.items():
        m=re.findall(p,text,re.I)
        if m: found[n]=list(set(m))
    return found

def detect_vpn_file(filename):
    if not filename: return False
    fn=filename.lower()
    for ext in VPN_EXTENSIONS:
        if fn.endswith(ext): return True
    return False

def detect_vpn_prefix(text):
    for p in VPN_PREFIXES:
        if p.lower() in text.lower(): return True
    return False

def bless(t,c):
    if t in ["vmess","vless","trojan","ssh","ss","ssr","hysteria","tuic"]:
        return c.startswith(f"{t}://")
    return True

def save_to_file(configs, filename, mode="a"):
    try:
        Path(filename).parent.mkdir(parents=True,exist_ok=True)
        with open(filename, mode, encoding="utf-8") as f:
            for c in configs:
                st="BLESSED" if c.get('blessed',True) else "RAW"
                ch=c.get('channel','unknown')
                cfg=c.get('config','')
                tp=c.get('type','UNKNOWN')
                ts=c.get('timestamp',datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                f.write(f"[{ts}] [{tp.upper()}] [{st}] {ch}\n{cfg}\n{'-'*40}\n")
        return True
    except Exception as e:
        notify("SAVE ERROR",str(e),R)
        return False

# ── FILE DOWNLOADER ────────────────────
async def download_file_full(message, prefix="dl"):
    if not message.media: return None,None
    doc=getattr(message.media,'document',None)
    if not doc: return None,None
    fname=""
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
    except:
        return fname,""

# ── DECRYPT VIA BOT (FIXED) ─────────────
async def decrypt_via_bot(client, message):
    try:
        notify("DECRYPT","Forwarding to decrypt bot...",Y)
        await client.forward_messages(DECRYPT_BOT, message)
        notify("DECRYPT","Waiting for bot to process...",Y)
        for attempt in range(12):
            await asyncio.sleep(5)
            async for response in client.iter_messages(DECRYPT_BOT, limit=3):
                if response.media and hasattr(response.media,'document'):
                    doc = response.media.document
                    fname = ""
                    for a in doc.attributes:
                        if hasattr(a,'file_name') and a.file_name:
                            fname = a.file_name
                            break
                    if fname.endswith('.txt') or doc.mime_type == "text/plain":
                        fname,content = await download_file_full(response,"decrypted")
                        if content and len(content) > 20:
                            notify("DECRYPT",f"SUCCESS: {len(content)} chars",G)
                            save_to_file([{"type":"DECRYPTED","config":content,"blessed":True,"channel":"decrypt_bot"}],"decrypted_configs.txt")
                            return content
                    if detect_vpn_file(fname):
                        continue
                if response.text and len(response.text) > 50:
                    if any(x in response.text.lower() for x in ['ssh://','vmess://','vless://','trojan://','host:','sni:']):
                        notify("DECRYPT",f"SUCCESS: {len(response.text)} chars",G)
                        save_to_file([{"type":"DECRYPTED","config":response.text,"blessed":True,"channel":"decrypt_bot"}],"decrypted_configs.txt")
                        return response.text
        notify("DECRYPT","No response after 60s",Y)
        return None
    except Exception as e:
        notify("DECRYPT ERROR",str(e),R)
        return None

# ── BOT TOKEN MANAGER ──────────────────
def get_bot_token():
    """Retrieve bot token from file or prompt user."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            token = f.read().strip()
            if token:
                return token
    print(f"\n  {Y}[!]{RES} No bot token found.")
    print(f"  {DIM}Get one from @BotFather on Telegram (send /newbot){RES}")
    token = input(f"  {Y}[?]{RES} Bot Token: ").strip()
    if token:
        with open(TOKEN_FILE,"w") as f:
            f.write(token)
        return token
    return None

async def get_bot_client():
    """Create and return authenticated bot client."""
    token = get_bot_token()
    if not token:
        print(f"  {R}[FATAL]{RES} Bot token required.")
        sys.exit(1)
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start(bot_token=token)
    return client

async def get_bot_info():
    """Get bot username for display."""
    try:
        client = await get_bot_client()
        me = await client.get_me()
        await client.disconnect()
        return me.username if me.username else me.first_name
    except:
        return None

# ── SCRAPERS ────────────────────────────
def scrape_public(channel,limit=50):
    notify("PUBLIC",f"Scraping @{channel}",C)
    spinner("Connecting",1.0)
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
                for line in extract_full_text(text):
                    if len(configs)>=limit: break
                    if detect_vpn_prefix(line):
                        configs.append({"type":"VPN_PREFIX","config":line,"blessed":True,"channel":channel,"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                        notify("VPN",line[:55],M)
                    found=extract_patterns(line)
                    for t,items in found.items():
                        for item in items:
                            if len(configs)>=limit: break
                            configs.append({"type":t,"config":item,"blessed":bless(t,item),"channel":channel,"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            last=msgs[-1].parent.get('data-post','')
            offset=int(last.split('/')[-1]) if last else None
            if not offset: break
        except Exception as e:
            notify("ERROR",str(e),R); break
    notify("DONE",f"{len(configs)} configs",G)
    return configs

async def scrape_private(client,channel,limit=100):
    notify("PRIVATE",f"Scraping {channel}",C)
    spinner("Reading",1.0)
    configs=[]; dec_configs=[]
    try:
        async for msg in client.iter_messages(channel, limit=limit):
            text=msg.text or ""
            if msg.media:
                doc=getattr(msg.media,'document',None)
                if doc:
                    fname=""
                    for a in doc.attributes:
                        if hasattr(a,'file_name'): fname=a.file_name; break
                    if detect_vpn_file(fname):
                        notify("VPN FILE",fname,M)
                        dec=await decrypt_via_bot(client,msg)
                        if dec:
                            dec_configs.append({"type":"DECRYPTED","config":dec,"blessed":True,"channel":channel,"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                            for line in dec.split('\n'):
                                line=line.strip()
                                if not line: continue
                                if detect_vpn_prefix(line):
                                    configs.append({"type":"VPN","config":line,"blessed":True,"channel":channel,"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                                found=extract_patterns(line)
                                for t,items in found.items():
                                    for item in items:
                                        configs.append({"type":t,"config":item,"blessed":bless(t,item),"channel":channel,"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                        continue
                    if doc.mime_type=="text/plain" or fname.endswith(('.txt','.log','.cfg','.conf','.json')):
                        _,content=await download_file_full(msg)
                        if content: text+="\n"+content; notify("TXT",f"Extracted {fname}",G)
            if not text.strip(): continue
            for line in extract_full_text(text):
                if detect_vpn_prefix(line):
                    configs.append({"type":"VPN_PREFIX","config":line,"blessed":True,"channel":channel,"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                found=extract_patterns(line)
                for t,items in found.items():
                    for item in items:
                        configs.append({"type":t,"config":item,"blessed":bless(t,item),"channel":channel,"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    except FloodWaitError as e:
        notify("FLOOD",f"Sleeping {e.seconds}s",Y); await asyncio.sleep(e.seconds)
    except Exception as e:
        notify("ERROR",str(e),R)
    notify("DONE",f"{len(configs)} configs + {len(dec_configs)} decrypted",G)
    return configs,dec_configs

# ── LIVE MESSAGE VIEWER ─────────────────
async def live_message_viewer(channel):
    client=await get_bot_client()
    notify("LIVE MSG",f"Viewing {channel} | Auto-Save ON | Auto-Decrypt ON",G)
    print(f"  {DIM}[CTRL+C to return]{RES}\n")
    @client.on(events.NewMessage(chats=channel))
    async def handler(event):
        ts=datetime.now().strftime("%H:%M:%S")
        text=event.message.text or ""
        if event.message.media:
            doc=getattr(event.message.media,'document',None)
            if doc:
                fname=""; size=0
                for a in doc.attributes:
                    if hasattr(a,'file_name'): fname=a.file_name
                size=doc.size
                if fname.endswith('.txt'):
                    _,content=await download_file_full(event.message,"live_txt")
                    if content:
                        save_to_file([{"type":"TXT_FILE","config":content,"blessed":True,"channel":channel}],"live_txt_saves.txt")
                        notify("SAVED TXT",f"{fname}",G)
                if detect_vpn_file(fname):
                    notify("VPN FILE",fname,M)
                    decrypted=await decrypt_via_bot(client,event.message)
                    if decrypted:
                        save_to_file([{"type":"DECRYPTED","config":decrypted,"blessed":True,"channel":channel}],"decrypted_configs.txt")
                        notify("DECRYPTED",fname,G)
                text=f"[FILE] {fname} ({size} bytes)"
        if text.strip():
            for line in text.split('\n')[:5]:
                print(f"  [{C}{ts}{RES}] {DIM}{line[:90]}{RES}")
        print(f"  {C}{'─'*tw()}{RES}")
    try:
        await client.run_until_disconnected()
    except KeyboardInterrupt:
        await client.disconnect()

# ── LIVE MONITOR ────────────────────────
async def live_monitor(channel):
    client=await get_bot_client()
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
                    dec=await decrypt_via_bot(client,event.message)
                    if dec: text+="\n"+dec; notify("DECRYPTED",fname,G)
                elif fname.endswith('.txt'):
                    _,content=await download_file_full(event.message)
                    if content: text+="\n"+content
        if not text.strip(): return
        for line in extract_full_text(text):
            found=extract_patterns(line)
            for t,items in found.items():
                for item in items:
                    notify(f"LIVE {t.upper()}",item[:55],G)
                    save_to_file([{"type":t,"config":item,"blessed":bless(t,item),"channel":channel}],"blessed_configs.txt")
    try:
        await client.run_until_disconnected()
    except KeyboardInterrupt:
        await client.disconnect()

# ── VIEW / EXPORT ──────────────────────
def view_saved(filename,title):
    if not os.path.exists(filename):
        print(f"  {DIM}No data.{RES}"); input(f"\n  {DIM}[Enter]{RES}"); return
    with open(filename,encoding="utf-8") as f:
        lines=[l.rstrip() for l in f if l.strip()]
    if not lines:
        print(f"  {DIM}Empty.{RES}"); input(f"\n  {DIM}[Enter]{RES}"); return
    page,total=0,(len(lines)//2+4)//5
    while True:
        os.system('clear')
        print(f"\n  {BG_C}{W}{BOLD}  {title}  {RES}")
        print(f"  {C}Page {page+1}/{max(total,1)}  [N]ext [P]rev [Q]uit{RES}\n")
        for i,line in enumerate(lines[page*5:(page+1)*5],page*5+1):
            print(f"  {DIM}[{i}]{RES} {line[:90]}")
        cmd=input(f"\n  {Y}[N/P/Q]{RES} ").strip().lower()
        if cmd in ('n','next') and page<total-1: page+=1
        elif cmd in ('p','prev') and page>0: page-=1
        elif cmd in ('q','quit'): break

def export_logs(filename,title):
    if not os.path.exists(filename):
        print(f"  {R}[!]{RES} No data."); input(f"\n  {DIM}[Enter]{RES}"); return
    out=input(f"  {Y}[?]{RES} Filename [export.json]: ").strip() or "export.json"
    if not out.endswith('.json'): out+='.json'
    configs=[]
    try:
        with open(filename,encoding="utf-8") as f:
            for line in f:
                line=line.strip()
                if line.startswith('['): configs.append({"entry":line})
                elif line and not line.startswith('-') and configs:
                    configs[-1]["content"]=line
        with open(out,"w",encoding="utf-8") as jf: json.dump(configs,jf,indent=2,ensure_ascii=False)
        notify("EXPORT",f"{len(configs)}
