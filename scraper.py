#!/usr/bin/env python3
# ============================================
# SCRAPER 2.0 TG — FINAL VERSION
# Created by Saeka Tojirp
# Live Auto-Save TXT | Auto-Decrypt VPN | Full TG Actions
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
from telethon.errors import FloodWaitError, SessionPasswordNeededError
from telethon.tl.functions.messages import SendMessageRequest, ForwardMessagesRequest
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest

API_ID=2040
API_HASH="b18441a1ff607e10a989891a5462e627"
SESSION_FILE=os.path.expanduser("~/.prvtspy_session")
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

# ── DECRYPT VIA BOT ─────────────────────
async def decrypt_via_bot(client, message):
    """Forward VPN file to decrypt bot and WAIT for .txt response. Extract and save full content."""
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

# ── SESSION ────────────────────────────
async def detect_login():
    if not os.path.exists(SESSION_FILE): return False
    try:
        c=TelegramClient(SESSION_FILE,API_ID,API_HASH)
        await c.start(); await c.disconnect()
        return True
    except: return False

async def create_session():
    if await detect_login():
        c=TelegramClient(SESSION_FILE,API_ID,API_HASH)
        await c.start(); me=await c.get_me()
        print(f"\n  {G}[WELCOME]{RES} {me.first_name} (@{me.username})")
        await c.disconnect(); return True,me
    print(f"\n  {Y}[!]{RES} No session found. One-time login.")
    phone=input(f"  {Y}[?]{RES} Phone (+63...): ").strip()
    if not phone: return False,None
    try:
        c=TelegramClient(SESSION_FILE,API_ID,API_HASH)
        await c.start(phone); me=await c.get_me()
        print(f"  {G}[SUCCESS]{RES} Logged in as: {me.first_name}")
        await c.disconnect(); return True,me
    except Exception as e:
        print(f"  {R}[ERROR]{RES} {e}")
        if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)
        return False,None

async def get_client():
    c=TelegramClient(SESSION_FILE,API_ID,API_HASH)
    await c.start(); return c

async def logout_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE); print(f"  {G}[OK]{RES} Session removed.")
    else: print(f"  {DIM}No session.{RES}")

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

# ── LIVE MESSAGE VIEWER (AUTO-SAVE + AUTO-DECRYPT) ──
async def live_message_viewer(channel):
    client=await get_client()
    notify("LIVE MSG",f"Viewing {channel} | Auto-Save ON | Auto-Decrypt ON",G)
    print(f"  {DIM}[CTRL+C to exit]{RES}\n")
    @client.on(events.NewMessage(chats=channel))
    async def handler(event):
        ts=datetime.now().strftime("%H:%M:%S")
        text=event.message.text or ""
        saved_files=[]
        decrypted_files=[]
        if event.message.media:
            doc=getattr(event.message.media,'document',None)
            if doc:
                fname=""; size=0
                for a in doc.attributes:
                    if hasattr(a,'file_name'): fname=a.file_name
                size=doc.size
                # Auto-save .txt files
                if fname.endswith('.txt'):
                    _,content=await download_file_full(event.message,"live_txt")
                    if content:
                        save_to_file([{"type":"TXT_FILE","config":content,"blessed":True,"channel":channel}],"live_txt_saves.txt")
                        saved_files.append(f"{fname} ({len(content)} chars)")
                        notify("SAVED TXT",f"{fname} -> live_txt_saves.txt",G)
                # Auto-detect VPN config files and decrypt
                if detect_vpn_file(fname):
                    notify("VPN FILE",fname,M)
                    decrypted=await decrypt_via_bot(client,event.message)
                    if decrypted:
                        save_to_file([{"type":"DECRYPTED","config":decrypted,"blessed":True,"channel":channel}],"decrypted_configs.txt")
                        decrypted_files.append(fname)
                        notify("DECRYPTED",f"{fname} -> decrypted_configs.txt",G)
                # Display file info
                text=f"[FILE] {fname} ({size} bytes)"
        if text.strip():
            for line in text.split('\n')[:5]:
                print(f"  [{C}{ts}{RES}] {DIM}{line[:90]}{RES}")
        if saved_files:
            for sf in saved_files:
                print(f"  [{G}SAVED{RES}] {sf}")
        if decrypted_files:
            for df in decrypted_files:
                print(f"  [{M}DECRYPTED{RES}] {df}")
        print(f"  {C}{'─'*tw()}{RES}")
    await client.run_until_disconnected()

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
    await client.run_until_disconnected()

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
        notify("EXPORT",f"{len(configs)} entries -> {out}",G)
    except Exception as e:
        notify("EXPORT ERROR",str(e),R)
    input(f"\n  {DIM}[Enter]{RES}")

# ── FULL TELEGRAM ACTIONS ──────────────
async def telegram_actions_menu():
    client=await get_client()
    me=await client.get_me()
    while True:
        os.system('clear')
        banner(me.first_name)
        print(f"  {G}[1]{RES} List Dialogs (Chats/Channels)")
        print(f"  {G}[2]{RES} Join Channel")
        print(f"  {G}[3]{RES} Leave Channel")
        print(f"  {G}[4]{RES} Send Message")
        print(f"  {G}[5]{RES} Forward Message")
        print(f"  {G}[6]{RES} View Last Messages")
        print(f"  {G}[7]{RES} Search Messages")
        print(f"  {G}[8]{RES} View My Profile")
        print(f"  {G}[9]{RES} Update Bio")
        print(f"  {G}[0]{RES} Back\n")
        ch=input(f"  {Y}[?]{RES} Choice: ").strip()
        if ch=='1':
            spinner("Fetching",1.0)
            dialogs=await client.get_dialogs(limit=20)
            for i,d in enumerate(dialogs):
                unread=f"{Y}[{d.unread_count}]{RES}" if d.unread_count else ""
                print(f"  {G}[{i+1}]{RES} {d.name} {unread}")
            input(f"\n  {DIM}[Enter]{RES}")
        elif ch=='2':
            c=input(f"  {Y}[?]{RES} Channel (@ or link): ").strip()
            try:
                await client(JoinChannelRequest(c))
                notify("JOINED",c,G)
            except Exception as e: notify("ERROR",str(e),R)
            time.sleep(1)
        elif ch=='3':
            c=input(f"  {Y}[?]{RES} Channel: ").strip()
            try:
                await client(LeaveChannelRequest(c))
                notify("LEFT",c,G)
            except Exception as e: notify("ERROR",str(e),R)
            time.sleep(1)
        elif ch=='4':
            c=input(f"  {Y}[?]{RES} To (channel/user): ").strip()
            txt=input(f"  {Y}[?]{RES} Message: ").strip()
            try:
                await client.send_message(c,txt)
                notify("SENT",f"Message sent to {c}",G)
            except Exception as e: notify("ERROR",str(e),R)
            time.sleep(1)
        elif ch=='5':
            c=input(f"  {Y}[?]{RES} From channel: ").strip()
            mid=int(input(f"  {Y}[?]{RES} Message ID: ").strip())
            to=input(f"  {Y}[?]{RES} To: ").strip()
            try:
                msg=await client.get_messages(c,ids=mid)
                await client.forward_messages(to,msg)
                notify("FORWARDED",f"Message {mid} -> {to}",G)
            except Exception as e: notify("ERROR",str(e),R)
            time.sleep(1)
        elif ch=='6':
            c=input(f"  {Y}[?]{RES} Channel: ").strip()
            lim=int(input(f"  {Y}[?]{RES} Count [10]: ") or "10")
            spinner("Loading",1.0)
            async for msg in client.iter_messages(c,limit=lim):
                sender=msg.sender.first_name if msg.sender else "Unknown"
                ts=msg.date.strftime("%Y-%m-%d %H:%M") if msg.date else ""
                txt=(msg.text or "[media]")[:80]
                print(f"  [{C}{ts}{RES}] {G}{sender}{RES}: {DIM}{txt}{RES}")
            input(f"\n  {DIM}[Enter]{RES}")
        elif ch=='7':
            c=input(f"  {Y}[?]{RES} Channel: ").strip()
            q=input(f"  {Y}[?]{RES} Search: ").strip()
            lim=int(input(f"  {Y}[?]{RES} Limit [20]: ") or "20")
            spinner("Searching",1.0)
            count=0
            async for msg in client.iter_messages(c,limit=lim,search=q):
                ts=msg.date.strftime("%Y-%m-%d %H:%M") if msg.date else ""
                txt=(msg.text or "[media]")[:80]
                print(f"  [{C}{ts}{RES}] {DIM}{txt}{RES}")
                count+=1
            print(f"  {G}Found: {count}{RES}")
            input(f"\n  {DIM}[Enter]{RES}")
        elif ch=='8':
            print(f"\n  {G}Name:{RES} {me.first_name} {me.last_name or ''}")
            print(f"  {G}Username:{RES} @{me.username}")
            print(f"  {G}Phone:{RES} {me.phone}")
            print(f"  {G}ID:{RES} {me.id}")
            print(f"  {G}Bio:{RES} {getattr(me,'about','N/A')}")
            input(f"\n  {DIM}[Enter]{RES}")
        elif ch=='9':
            bio=input(f"  {Y}[?]{RES} New bio: ").strip()
            try:
                await client(UpdateProfileRequest(about=bio))
                notify("UPDATED","Bio updated",G)
            except Exception as e: notify("ERROR",str(e),R)
            time.sleep(1)
        elif ch=='0': break
    await client.disconnect()

# ── MENUS ──────────────────────────────
def main_menu():
    print(f"  {G}[1]{RES} Scrape Telegram Channels")
    print(f"  {G}[2]{RES} View Saved Logs")
    print(f"  {G}[3]{RES} Export Saved Logs")
    print(f"  {G}[4]{RES} Recent Channels")
    print(f"  {G}[5]{RES} Live Message Viewer (Auto-Save + Decrypt)")
    print(f"  {G}[6]{RES} Live Monitor (Auto-Scrape)")
    print(f"  {G}[7]{RES} Telegram Actions")
    print(f"  {G}[8]{RES} Change Session")
    print(f"  {G}[0]{RES} Exit\n")
    return input(f"  {Y}[?]{RES} Choice: ").strip()

async def scrape_menu():
    os.system('clear')
    banner(current_user)
    print(f"  {G}[1]{RES} Public Channel")
    print(f"  {G}[2]{RES} Private Channel (Decrypt VPN Files)")
    if RECENT_CHANNELS:
        print(f"\n  {M}Recent:{RES}")
        for i,rc in enumerate(RECENT_CHANNELS[:5]):
            print(f"  {G}[r{i+1}]{RES} {rc}")
    print(f"\n  {G}[0]{RES} Back\n")
    ch=input(f"  {Y}[?]{RES} Choice: ").strip()
    if ch.startswith('r') and ch[1:].isdigit():
        idx=int(ch[1:])-1
        if 0<=idx<len(RECENT_CHANNELS):
            ch_name=RECENT_CHANNELS[idx]; save_recent(ch_name)
            lim=int(input(f"  {Y}[?]{RES} Limit [50]: ") or "50")
            cfgs=scrape_public(ch_name,lim)
            if cfgs: save_to_file(cfgs,"blessed_configs.txt")
    elif ch=='1':
        ch_name=input(f"  {Y}[?]{RES} Channel: ").replace("@","").replace("t.me/","")
        save_recent(ch_name)
        lim=int(input(f"  {Y}[?]{RES} Limit [50]: ") or "50")
        cfgs=scrape_public(ch_name,lim)
        if cfgs: save_to_file(cfgs,"blessed_configs.txt")
    elif ch=='2':
        ch_name=input(f"  {Y}[?]{RES} Channel: "); save_recent(ch_name)
        lim=int(input(f"  {Y}[?]{RES} Limit [100]: ") or "100")
        client=await get_client()
        cfgs,dec=await scrape_private(client,ch_name,lim)
        if cfgs: save_to_file(cfgs,"blessed_configs.txt")
        if dec: save_to_file(dec,"decrypted_configs.txt")
        await client.disconnect()
    input(f"\n  {DIM}[Enter]{RES}")

current_user=""

async def main():
    global current_user
    load_recent()
    if not await detect_login():
        ok,me=await create_session()
        if not ok:
            print(f"  {R}[FATAL]{RES} Login required."); sys.exit(1)
        current_user=me.first_name if me else ""
    else:
        client=TelegramClient(SESSION_FILE,API_ID,API_HASH)
        await client.start()
        me=await client.get_me()
        current_user=me.first_name if me else ""
        print(f"\n  {G}[WELCOME]{RES} {me.first_name} (@{me.username})")
        await client.disconnect(); time.sleep(1.5)
    
    while True:
        os.system('clear'); banner(current_user); choice=main_menu()
        if choice=='0': pulse_glow(" GOODBYE! ",3,0.3); break
        elif choice=='1': await scrape_menu()
        elif choice=='2':
            os.system('clear'); banner(current_user)
            print(f"  {G}[1]{RES} Blessed Configs\n  {G}[2]{RES} Decrypted\n  {G}[3]{RES} VPN Protocols\n  {G}[4]{RES} Live TXT Saves\n  {G}[0]{RES} Back\n")
            v=input(f"  {Y}[?]{RES} ").strip()
            if v=='1': view_saved("blessed_configs.txt","BLESSED CONFIGS")
            elif v=='2': view_saved("decrypted_configs.txt","DECRYPTED")
            elif v=='3': view_saved("vpn_protocols.txt","VPN PROTOCOLS")
            elif v=='4': view_saved("live_txt_saves.txt","LIVE TXT SAVES")
        elif choice=='3':
            os.system('clear'); banner(current_user)
            print(f"  {G}[1]{RES} Blessed\n  {G}[2]{RES} Decrypted\n  {G}[3]{RES} VPN Protocols\n  {G}[4]{RES} Live TXT\n  {G}[0]{RES} Back\n")
            e=input(f"  {Y}[?]{RES} ").strip()
            if e=='1': export_logs("blessed_configs.txt","BLESSED")
            elif e=='2': export_logs("decrypted_configs.txt","DECRYPTED")
            elif e=='3': export_logs("vpn_protocols.txt","VPN PROTOCOLS")
            elif e=='4': export_logs("live_txt_saves.txt","LIVE TXT")
        elif choice=='4':
            os.system('clear'); banner(current_user)
            if RECENT_CHANNELS:
                for i,rc in enumerate(RECENT_CHANNELS): print(f"  {G}[{i+1}]{RES} {rc}")
            else: print(f"  {DIM}No recent.{RES}")
            input(f"\n  {DIM}[Enter]{RES}")
        elif choice=='5':
            c=input(f"  {Y}[?]{RES} Channel: ").strip(); save_recent(c)
            await live_message_viewer(c)
        elif choice=='6':
            c=input(f"  {Y}[?]{RES} Channel: ").strip(); save_recent(c)
            await live_monitor(c)
        elif choice=='7': await telegram_actions_menu()
        elif choice=='8':
            await logout_session()
            ok,me=await create_session()
            if ok: current_user=me.first_name if me else ""
        else: print(f"  {R}[!]{RES} Invalid"); time.sleep(0.5)

if __name__=="__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print(f"\n  {M}[END]{RES}\n"); sys.exit(0)
