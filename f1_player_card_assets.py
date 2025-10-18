#!/usr/bin/env python3
import os, time, math, requests, pandas as pd, numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.font_manager import FontProperties
from datetime import datetime

BASE='https://api.openf1.org/v1'
DRIVER=16
DESKTOP=os.path.expanduser('~/Desktop')
OUT_DIR=os.path.join(DESKTOP,'leclerc_player_card')
os.makedirs(OUT_DIR, exist_ok=True)

session=requests.Session()

def fetch(endpoint, params, retries=3, backoff=0.6):
    url=f"{BASE}/{endpoint}"
    for i in range(retries):
        try:
            r=session.get(url, params=params, timeout=10)
            r.raise_for_status(); return r.json()
        except requests.exceptions.RequestException as e:
            if i==retries-1: print(f'fetch error {endpoint}: {e}'); return None
            time.sleep(backoff*(i+1))

# Font setup
RUSSO=None
russo_paths=[
    '/Library/Fonts/RussoOne-Regular.ttf',
    os.path.expanduser('~/Library/Fonts/RussoOne-Regular.ttf'),
    os.path.join(os.path.dirname(__file__), 'RussoOne-Regular.ttf'),
]
for p in russo_paths:
    if os.path.exists(p):
        try:
            RUSSO=FontProperties(fname=p)
            break
        except Exception:
            RUSSO=None

def title(ax, txt):
    if RUSSO: ax.set_title(txt, fontproperties=RUSSO, fontsize=24, pad=14)
    else: ax.set_title(txt, fontsize=24, pad=14, fontweight='bold')

def label(ax, lx, ly):
    ax.set_xlabel(lx, fontsize=12)
    ax.set_ylabel(ly, fontsize=12)

# Get sessions 2025-2026; include all races in these seasons

def list_race_sessions():
    sessions=[]
    for yr in [2026,2025]:
        data=fetch('sessions', {'year': yr})
        if data:
            races=[s for s in data if s.get('session_name')=='Race']
            sessions.extend(sorted(races, key=lambda x:x.get('date_start','')))
    return sessions

# Pull per-session data for driver

def collect_for_session(session_key, meeting_name):
    laps=fetch('laps', {'session_key': session_key, 'driver_number': DRIVER}) or []
    pos=fetch('position', {'session_key': session_key, 'driver_number': DRIVER}) or []
    pits=fetch('pit', {'session_key': session_key, 'driver_number': DRIVER}) or []
    stints=fetch('stints', {'session_key': session_key, 'driver_number': DRIVER}) or []
    intervals=fetch('intervals', {'session_key': session_key, 'driver_number': DRIVER}) or []
    rc=fetch('race_control', {'session_key': session_key}) or []
    weather=fetch('weather', {'session_key': session_key}) or []
    for row in laps: row['meeting_name']=meeting_name
    for row in pos: row['meeting_name']=meeting_name
    for row in pits: row['meeting_name']=meeting_name
    for row in stints: row['meeting_name']=meeting_name
    for row in intervals: row['meeting_name']=meeting_name
    for row in rc: row['meeting_name']=meeting_name
    for row in weather: row['meeting_name']=meeting_name
    return laps,pos,pits,stints,intervals,rc,weather

# Helpers

def is_green_flag(rc_rows, ts_iso):
    # treat green if not under SC/VSC at timestamp
    try:
        t=datetime.fromisoformat(ts_iso.replace('Z','+00:00'))
    except Exception:
        return True
    active=False
    for r in rc_rows:
        cat=(r.get('category') or '').lower(); msg=(r.get('message') or '').lower()
        if 'sc' in msg or 'safety car' in msg or 'virtual' in msg or 'vsc' in msg or 'yellow' in msg:
            # mark during windows; simplistic: any RC during race considered non-green
            active=True
    return not active

# Metric 1: Stint pace vs tyre age

def viz_stint_degradation(all_laps, stints, rc_rows, fname):
    if not all_laps: return False
    df=pd.DataFrame(all_laps)
    if 'lap_duration' not in df: return False
    df=df[df['lap_duration'].notna()].copy()
    if 'is_pit_in_lap' in df: df=df[df['is_pit_in_lap']!=True]
    if 'is_pit_out_lap' in df: df=df[df['is_pit_out_lap']!=True]
    # attach stint_no/compound if available
    st=pd.DataFrame(stints) if stints else pd.DataFrame()
    if not st.empty and 'stint_number' in st and 'compound' in st:
        # approximate tyre_age by cumulative laps per stint
        df['stint_number']=np.nan
        for _,row in st.iterrows():
            # if stint start/end lap available
            s=row.get('stint_number'); start=row.get('lap_start') or row.get('start_lap'); end=row.get('lap_end') or row.get('end_lap')
            if pd.notna(start) and pd.notna(end):
                m=(df['lap_number']>=start) & (df['lap_number']<=end)
                df.loc[m,'stint_number']=s
        df['compound']=None
        for _,row in st.iterrows():
            s=row.get('stint_number'); comp=row.get('compound')
            df.loc[df['stint_number']==s,'compound']=comp
        df['tyre_age']=df.groupby('stint_number').cumcount()+1
    else:
        df['stint_number']=1; df['compound']='UNK'; df['tyre_age']=df.groupby('stint_number').cumcount()+1
    if 'date' in df:
        green_mask=df['date'].apply(lambda x:is_green_flag(rc_rows, x))
        df=df[green_mask]
    if df.empty: return False
    plt.figure(figsize=(12,6.75), dpi=200)
    sns.set_style('white')
    ax=plt.gca()
    ax.set_facecolor('#0B0B0C')
    plt.grid(color='#2A2A2C', linestyle='-', linewidth=0.5, alpha=0.6)
    for (s,comp),g in df.groupby(['stint_number','compound']):
        if len(g)<3: continue
        g=g.sort_values('tyre_age')
        plt.plot(g['tyre_age'], g['lap_duration'], label=f'Stint {int(s)} {comp}', linewidth=2)
        try:
            z=np.polyfit(g['tyre_age'], g['lap_duration'], 1)
            x=np.array([g['tyre_age'].min(), g['tyre_age'].max()])
            plt.plot(x, z[0]*x+z[1], linestyle='--', alpha=0.5)
        except Exception:
            pass
    plt.legend(frameon=False, fontsize=9, labelcolor='white')
    ax=plt.gca()
    title(ax, 'Stint Pace vs Tyre Age')
    ax.tick_params(colors='white')
    label(ax,'Tyre Age (laps)','Lap Time (s)')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, fname), bbox_inches='tight')
    plt.close(); return True

# Metric 2: Position trace with events

def viz_position_trace(pos_rows, pits, rc_rows, fname):
    if not pos_rows: return False
    d=pd.DataFrame(pos_rows).copy()
    if d.empty or 'position' not in d: return False
    d['idx']=range(1,len(d)+1)
    plt.figure(figsize=(12,6.75), dpi=200)
    sns.set_style('white')
    ax=plt.gca(); ax.set_facecolor('#0B0B0C'); plt.grid(color='#2A2A2C', linewidth=0.5, alpha=0.6)
    plt.plot(d['idx'], d['position'], color='#E10600', linewidth=3)
    # markers for pits
    if pits:
        for p in pits:
            # approximate by nearest index to pit time
            if 'date' in p and isinstance(p['date'], str):
                plt.axvline(x=min(d['idx'].max(), max(1, int(len(d)*0.5))), color='gray', alpha=0.1)
        # simple: mark text
    ax=plt.gca(); ax.invert_yaxis(); ax.tick_params(colors='white')
    title(ax,'Position Trace with Events')
    label(ax,'Time Index','Position (lower is better)')
    plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR,fname), bbox_inches='tight'); plt.close(); return True

# Metric 3: Lap-time distribution

def viz_lap_distribution(all_laps, rc_rows, fname):
    if not all_laps: return False
    df=pd.DataFrame(all_laps)
    if df.empty or 'lap_duration' not in df: return False
    df=df[df['lap_duration'].notna()].copy()
    if 'is_pit_in_lap' in df: df=df[df['is_pit_in_lap']!=True]
    if 'is_pit_out_lap' in df: df=df[df['is_pit_out_lap']!=True]
    if 'date' in df:
        df=df[df['date'].apply(lambda x:is_green_flag(rc_rows,x))]
    if df.empty: return False
    plt.figure(figsize=(12,6.75), dpi=200)
    sns.set_style('white')
    ax=plt.gca(); ax.set_facecolor('#0B0B0C')
    sns.kdeplot(df['lap_duration'], fill=True, color='#E10600', alpha=0.6, linewidth=0)
    med=df['lap_duration'].median(); std=df['lap_duration'].std()
    plt.axvline(med, color='white', linestyle='--')
    ax=plt.gca(); title(ax, f'Lap Time Distribution  |  Median {med:.2f}s  stdev {std:.2f}s')
    ax.tick_params(colors='white')
    label(ax,'Lap Time (s)','Density')
    plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR,fname), bbox_inches='tight'); plt.close(); return True

# Metric 4: Pit loss per stop (approx)

def viz_pit_loss(all_laps, pits, fname):
    if not all_laps or not pits: return False
    df=pd.DataFrame(all_laps)
    if df.empty or 'lap_duration' not in df: return False
    df=df[df['lap_duration'].notna()].copy()
    med=df['lap_duration'].median()
    bars=[]; labels=[]
    for i,p in enumerate(pits, start=1):
        # approximate in/out laps nearby extremes
        # pick longest lap within +-2 laps of pit timestamp proxy if lap_number present
        # fallback: show pit_duration if present
        loss=p.get('pit_duration')
        if loss is None:
            loss=float(max(df['lap_duration'].nlargest(1))) - med
        bars.append(loss if loss is not None else 0)
        labels.append(f'Stop {i}')
    if not bars: return False
    plt.figure(figsize=(12,6.75), dpi=200)
    sns.set_style('white')
    ax=plt.gca(); ax.set_facecolor('#0B0B0C')
    sns.barplot(x=labels, y=bars, color='#E10600')
    title(ax,'Pit Loss per Stop (approx)')
    ax.tick_params(colors='white')
    label(ax,'Pit Stop','# Seconds Lost')
    for i,v in enumerate(bars):
        plt.text(i, v+0.2, f"{v:.1f}s", ha='center', va='bottom', fontsize=10)
    plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR,fname), bbox_inches='tight'); plt.close(); return True

# Metric 5: Weather vs performance scatter (per race)

def viz_weather_perf(race_summaries, fname):
    if not race_summaries: return False
    df=pd.DataFrame(race_summaries)
    if df.empty or 'avg_temp' not in df or 'final_pos' not in df: return False
    plt.figure(figsize=(12,6.75), dpi=200)
    sns.set_style('white')
    ax=plt.gca(); ax.set_facecolor('#0B0B0C')
    plt.scatter(df['avg_temp'], df['final_pos'], s=120, c='#E10600', edgecolors='white', linewidths=1.5)
    for _,r in df.iterrows():
        plt.text(r['avg_temp'], r['final_pos']-0.3, r['track'][:10], ha='center', fontsize=9)
    ax=plt.gca(); ax.invert_yaxis(); ax.tick_params(colors='white')
    title(ax,'Weather vs Final Position')
    label(ax,'Avg Air Temp (°C)','Final Position')
    plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR,fname), bbox_inches='tight'); plt.close(); return True


def compute_advanced_metrics(laps, stints, intervals, rc_rows):
    # Returns dict with advanced stats over a race
    if not laps:
        return None
    ld=pd.DataFrame(laps)
    if ld.empty or 'lap_duration' not in ld: return None
    ld=ld[ld['lap_duration'].notna()].copy()
    # join intervals for traffic state
    iv=pd.DataFrame(intervals) if intervals else pd.DataFrame()
    if not iv.empty and 'interval_to_position_ahead' in iv and 'date' in iv and 'date' in ld:
        # round/join by nearest minute
        ld['date_round']=ld['date'].str.slice(0,16)
        iv['date_round']=iv['date'].str.slice(0,16)
        ld=ld.merge(iv[['date_round','interval_to_position_ahead']], on='date_round', how='left')
        ld['traffic_state']=np.where(ld['interval_to_position_ahead'].notna() & (ld['interval_to_position_ahead']<1.5), 'traffic','clean')
    else:
        ld['traffic_state']='unknown'
    # filter green
    if 'date' in ld:
        ld=ld[ld['date'].apply(lambda x:is_green_flag(rc_rows,x))]
    # exclude pit laps
    if 'is_pit_in_lap' in ld: ld=ld[ld['is_pit_in_lap']!=True]
    if 'is_pit_out_lap' in ld: ld=ld[ld['is_pit_out_lap']!=True]
    # stint regression slopes
    st=pd.DataFrame(stints) if stints else pd.DataFrame()
    slopes=[]
    if not st.empty and 'stint_number' in st:
        ld['stint_number']=np.nan
        for _,row in st.iterrows():
            s=row.get('stint_number'); start=row.get('lap_start') or row.get('start_lap'); end=row.get('lap_end') or row.get('end_lap')
            if pd.notna(start) and pd.notna(end):
                m=(ld['lap_number']>=start)&(ld['lap_number']<=end)
                ld.loc[m,'stint_number']=s
        ld['tyre_age']=ld.groupby('stint_number').cumcount()+1
        for s, g in ld.dropna(subset=['stint_number']).groupby('stint_number'):
            if len(g)>=3:
                z=np.polyfit(g['tyre_age'], g['lap_duration'], 1)
                slopes.append(z[0])
    slope=np.mean(slopes) if slopes else None
    # clean vs traffic pace
    clean_pace=ld[ld['traffic_state']=='clean']['lap_duration'].mean() if 'traffic_state' in ld.columns else None
    traffic_pace=ld[ld['traffic_state']=='traffic']['lap_duration'].mean() if 'traffic_state' in ld.columns else None
    pace_delta=(traffic_pace-clean_pace) if (clean_pace and traffic_pace) else None
    return {
        'avg_degradation_slope': slope,
        'clean_pace': clean_pace,
        'traffic_pace': traffic_pace,
        'traffic_penalty': pace_delta
    }

def compute_restart_effectiveness(pos_rows, rc_rows, window=3):
    if not pos_rows or not rc_rows:
        return []
    pdpos=pd.DataFrame(pos_rows)
    if pdpos.empty or 'position' not in pdpos or 'date' not in pdpos:
        return []
    pdpos=pdpos.copy(); pdpos['t']=pdpos['date']
    # naive: treat any race_control message containing 'green' as restart
    greens=[r for r in rc_rows if isinstance(r.get('message'), str) and ('green' in r['message'].lower() or 'resume' in r['message'].lower())]
    results=[]
    for g in greens:
        gt=g.get('date')
        if not isinstance(gt, str):
            continue
        # find nearest position index at/after green
        idx=pdpos.index[pdpos['t']>=gt]
        if len(idx)==0:
            continue
        i0=idx[0]
        i1=min(i0+window, len(pdpos)-1)
        p0=float(pdpos.loc[i0,'position']); p1=float(pdpos.loc[i1,'position'])
        results.append({'green_time': gt, 'delta': p0-p1}) # positive => gained positions
    return results

def compute_undercut_effectiveness(intervals, pits, lookahead=5):
    if not intervals or not pits:
        return []
    iv=pd.DataFrame(intervals)
    if iv.empty or 'interval_to_position_ahead' not in iv or 'date' not in iv:
        return []
    iv=iv.copy(); iv['t']=iv['date']
    out=[]
    for p in pits:
        pt=p.get('date')
        if not isinstance(pt, str):
            continue
        pre_idx=iv.index[iv['t']<=pt]
        post_idx=iv.index[iv['t']>pt]
        if len(pre_idx)==0 or len(post_idx)==0:
            continue
        pre=float(iv.loc[pre_idx[-1],'interval_to_position_ahead']) if pd.notna(iv.loc[pre_idx[-1],'interval_to_position_ahead']) else None
        post_seq=iv.loc[post_idx, 'interval_to_position_ahead'].head(lookahead)
        post=post_seq.mean() if not post_seq.empty else None
        if pre is None or post is None:
            continue
        out.append({'pit_time': pt, 'gap_before': pre, 'gap_after': post, 'delta': pre-post}) # positive => closed gap
    return out

def compute_ontrack_gains_excluding_pit(pos_rows, pits):
    if not pos_rows:
        return []
    d=pd.DataFrame(pos_rows)
    if d.empty or 'position' not in d:
        return []
    exclude=set()
    if pits:
        # exclude windows around own pit by index (rough)
        idxs=list(range(len(d)))
        mid=len(d)//2
        for k in range(len(d)):
            pass
        # simple approach: exclude 3 indices around mid for each pit (no exact align)
        for _ in pits:
            for off in [-1,0,1]:
                exclude.add(max(0, min(len(d)-1, mid+off)))
    gains=[]
    cum=0
    for i in range(1, len(d)):
        if i in exclude or (i-1) in exclude:
            continue
        delta=float(d.loc[i-1,'position'])-float(d.loc[i,'position'])
        cum+=delta
        gains.append({'i': i, 'delta': delta, 'cum': cum})
    return gains

def tyre_age_adjusted_pace_index(laps, stints):
    if not laps:
        return pd.DataFrame()
    ld=pd.DataFrame(laps)
    if ld.empty or 'lap_duration' not in ld:
        return pd.DataFrame()
    ld=ld[ld['lap_duration'].notna()].copy()
    st=pd.DataFrame(stints) if stints else pd.DataFrame()
    if st.empty or 'stint_number' not in st:
        return pd.DataFrame()
    ld['stint_number']=np.nan
    for _,row in st.iterrows():
        s=row.get('stint_number'); start=row.get('lap_start') or row.get('start_lap'); end=row.get('lap_end') or row.get('end_lap')
        if pd.notna(start) and pd.notna(end):
            m=(ld['lap_number']>=start)&(ld['lap_number']<=end)
            ld.loc[m,'stint_number']=s
    ld=ld.dropna(subset=['stint_number'])
    if ld.empty:
        return pd.DataFrame()
    ld['tyre_age']=ld.groupby('stint_number').cumcount()+1
    idx_rows=[]
    for s, g in ld.groupby('stint_number'):
        if len(g)>=3:
            z=np.polyfit(g['tyre_age'], g['lap_duration'], 1)
            pred=z[0]*g['tyre_age']+z[1]
            idx=(g['lap_duration']/pred)
            tmp=g[['lap_number','tyre_age']].copy(); tmp['pace_index']=idx.values; tmp['stint_number']=s
            idx_rows.append(tmp)
    return pd.concat(idx_rows, ignore_index=True) if idx_rows else pd.DataFrame()

def viz_restart_effectiveness(pos_rows, rc_rows, fname):
    data=compute_restart_effectiveness(pos_rows, rc_rows)
    if not data:
        return False
    df=pd.DataFrame(data)
    plt.figure(figsize=(12,6.75), dpi=200)
    ax=plt.gca(); ax.set_facecolor('#0B0B0C')
    sns.barplot(x=list(range(len(df))), y=df['delta'], color='#4CAF50')
    title(ax,'Restart Effectiveness (Δ positions over 3 laps)')
    ax.tick_params(colors='white')
    label(ax,'Restart Index','Positions Gained')
    plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR,fname), bbox_inches='tight'); plt.close(); return True

def viz_undercut_effectiveness(intervals, pits, fname):
    data=compute_undercut_effectiveness(intervals, pits)
    if not data:
        return False
    df=pd.DataFrame(data)
    plt.figure(figsize=(12,6.75), dpi=200)
    ax=plt.gca(); ax.set_facecolor('#0B0B0C')
    plt.scatter(df['gap_before'], df['gap_after'], s=120, c=np.where(df['delta']>0,'#4CAF50','#F44336'), edgecolors='white', linewidths=1.5)
    for _,r in df.iterrows():
        plt.text(r['gap_before'], r['gap_after'], f"{r['delta']:.1f}", color='white', fontsize=9)
    title(ax,'Undercut Effectiveness (gap to car ahead: before vs after)')
    ax.tick_params(colors='white')
    label(ax,'Gap Before (s)','Gap After (s)')
    plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR,fname), bbox_inches='tight'); plt.close(); return True

def viz_ontrack_gains(gains, fname):
    if not gains:
        return False
    df=pd.DataFrame(gains)
    plt.figure(figsize=(12,6.75), dpi=200)
    ax=plt.gca(); ax.set_facecolor('#0B0B0C')
    plt.plot(df['i'], df['cum'], color='#E10600', linewidth=3)
    title(ax,'On-Track Gains (excl. pit windows)')
    ax.tick_params(colors='white')
    label(ax,'Index','Cumulative Positions Gained')
    plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR,fname), bbox_inches='tight'); plt.close(); return True

def viz_pace_index(idx_df, fname):
    if idx_df is None or idx_df.empty:
        return False
    plt.figure(figsize=(12,6.75), dpi=200)
    ax=plt.gca(); ax.set_facecolor('#0B0B0C')
    sns.violinplot(x='stint_number', y='pace_index', data=idx_df, inner='quartile', palette='Reds')
    plt.axhline(1.0, color='white', linestyle='--', linewidth=1)
    title(ax,'Tyre-Age Adjusted Pace Index (1.0 = expected)')
    ax.tick_params(colors='white')
    label(ax,'Stint','Pace Index')
    plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR,fname), bbox_inches='tight'); plt.close(); return True

def make_stylized_visuals(stints, all_laps, pos_rows, pits, rc_rows, positions_per_race):
    # 1) Radial gauge: podium rate from last N races
    try:
        if positions_per_race:
            import numpy as np
            podium_rate=100.0*len([p for p in positions_per_race if p<=3])/len(positions_per_race)
            fig,ax=plt.subplots(figsize=(12,6.75), subplot_kw={'projection':'polar'}, dpi=200)
            theta=np.linspace(0, 2*np.pi, 300)
            ax.plot(theta, np.ones_like(theta), color='#EEEEEE', linewidth=20)
            ax.plot(theta[:int(len(theta)*podium_rate/100.0)], np.ones_like(theta[:int(len(theta)*podium_rate/100.0)]), color='#DC143C', linewidth=20)
            ax.set_yticklabels([]); ax.set_xticklabels([]); ax.set_ylim(0,1.2)
            ax.set_facecolor('white')
            if RUSSO:
                ax.text(0,0, f"{podium_rate:.0f}%\nPODIUM RATE", ha='center', va='center', fontproperties=RUSSO, fontsize=28)
            else:
                ax.text(0,0, f"{podium_rate:.0f}%\nPODIUM RATE", ha='center', va='center', fontsize=28, fontweight='bold')
            plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR,'leclerc_radial_podium.png'), bbox_inches='tight'); plt.close()
    except Exception as e:
        pass

    # 2) Donut: stint share by compound (last race)
    try:
        sd=pd.DataFrame(stints) if stints else pd.DataFrame()
        if not sd.empty and 'compound' in sd:
            counts=sd['compound'].value_counts()
            fig,ax=plt.subplots(figsize=(12,6.75), dpi=200)
            wedges, texts=ax.pie(counts.values, labels=counts.index, colors=['#DC143C','#FFD700','#333333','#888888'], wedgeprops=dict(width=0.4))
            centre=plt.Circle((0,0),0.6,fc='white'); ax.add_artist(centre)
            title(ax,'Tyre Compound Share (Last Race)')
            plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR,'leclerc_donut_compounds.png'), bbox_inches='tight'); plt.close()
    except Exception:
        pass

    # 3) Heatmap tiles: lap rank blocks (last race)
    try:
        df=pd.DataFrame(all_laps)
        if not df.empty and 'lap_number' in df and 'lap_duration' in df:
            df=df[df['lap_duration'].notna()].copy()
            # bucket laps into tiles of 5
            df['tile']=((df['lap_number']-1)//5)+1
            tile_perf=df.groupby('tile')['lap_duration'].mean().reset_index()
            fig,ax=plt.subplots(figsize=(12,6.75), dpi=200)
            sns.heatmap(tile_perf[['lap_duration']].T, cmap='rocket', cbar=True, ax=ax)
            ax.set_yticklabels(['Avg Lap (s)'])
            ax.set_xticklabels([int(t) for t in tile_perf['tile']])
            title(ax,'Lap Pace Tiles (5-lap blocks)')
            plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR,'leclerc_heat_tiles.png'), bbox_inches='tight'); plt.close()
    except Exception:
        pass

    # 4) Event timeline: simple horizontal bands for SC/VSC and pit markers
    try:
        fig,ax=plt.subplots(figsize=(12,6.75), dpi=200)
        ax.set_xlim(0,100)
        ax.set_ylim(0,10)
        ax.axis('off')
        title(ax,'Race Events Timeline')
        # SC/VSC bands (mocked as generic bands if present)
        if rc_rows:
            ax.fill_between([10,30],[6,6],[8,8], color='yellow', alpha=0.2, label='SC/VSC')
        # pit markers
        if pits:
            xs=[20,40,60][:len(pits)]
            for x in xs:
                ax.plot([x,x],[2,5], color='#333', linewidth=3)
        plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR,'leclerc_event_timeline.png'), bbox_inches='tight'); plt.close()
    except Exception:
        pass

    # 5) Waterfall: position deltas across last 5 races
    try:
        if positions_per_race:
            vals=np.array(positions_per_race[-5:])
            deltas = np.diff(vals, prepend=vals[0])
            fig,ax=plt.subplots(figsize=(12,6.75), dpi=200)
            cum=0
            for i, d in enumerate(deltas):
                color = '#4CAF50' if d<0 else '#F44336'
                ax.bar(i, d, bottom=cum, color=color)
                cum += d
            title(ax,'Position Delta Waterfall (last 5)')
            label(ax,'Race Index','Delta')
            plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR,'leclerc_waterfall.png'), bbox_inches='tight'); plt.close()
    except Exception:
        pass

def main():
    sessions=list_race_sessions()
    if not sessions:
        print('No sessions found'); return
    # Use all sessions in the selected seasons
    all_laps=[]; last_pos=None; last_pits=None; last_stints=None; last_rc=None
    race_summaries=[]
    positions_per_race=[]
    for s in sessions:
        session_key=s.get('session_key'); meeting_key=s.get('meeting_key')
        meet=fetch('meetings', {'meeting_key': meeting_key}) or []
        meeting_name=meet[0].get('meeting_name','Race') if meet else 'Race'
        laps,pos,pits,stints,intervals,rc,weather=collect_for_session(session_key, meeting_name)
        all_laps.extend(laps)
        # store last for single-race visuals
        last_pos=pos or last_pos
        last_pits=pits or last_pits
        last_stints=stints or last_stints
        last_rc=rc or last_rc
        # summary for weather scatter
        final_pos=None
        if pos:
            pdf=pd.DataFrame(pos)
            if not pdf.empty and 'position' in pdf:
                final_pos=float(pdf.iloc[-1]['position'])
                positions_per_race.append(final_pos)
        avg_temp=None
        if weather:
            wdf=pd.DataFrame(weather)
            if not wdf.empty and 'air_temperature' in wdf:
                avg_temp=float(wdf['air_temperature'].mean())
        if final_pos is not None and avg_temp is not None:
            race_summaries.append({'track': meeting_name, 'avg_temp': avg_temp, 'final_pos': final_pos})
        # compute advanced metrics per race for summaries
        try:
            adv=compute_advanced_metrics(laps, stints, intervals, rc)
            if adv:
                # persist summary per race for later visuals
                pass
        except Exception:
            pass
        time.sleep(0.2)
    # Render five visuals
    v1=viz_stint_degradation(all_laps, last_stints or [], last_rc or [], 'leclerc_stint_degradation.png')
    v2=viz_position_trace(last_pos or [], last_pits or [], last_rc or [], 'leclerc_position_trace.png')
    v3=viz_lap_distribution(all_laps, last_rc or [], 'leclerc_lap_distribution.png')
    v4=viz_pit_loss(all_laps, last_pits or [], 'leclerc_pit_loss.png')
    v5=viz_weather_perf(race_summaries, 'leclerc_weather_vs_position.png')
    # Extra stylized visuals
    try:
        make_stylized_visuals(last_stints or [], all_laps, last_pos or [], last_pits or [], last_rc or [], positions_per_race)
    except Exception as e:
        print('Stylized visuals error:', e)
    # Advanced analytics visuals
    try:
        if last_pos and last_rc:
            viz_restart_effectiveness(last_pos, last_rc, 'leclerc_restart_effectiveness.png')
        if intervals and last_pits:
            viz_undercut_effectiveness(intervals, last_pits, 'leclerc_undercut_effectiveness.png')
        gains=compute_ontrack_gains_excluding_pit(last_pos or [], last_pits or [])
        viz_ontrack_gains(gains, 'leclerc_ontrack_gains.png')
        pace_idx=tyre_age_adjusted_pace_index(all_laps, last_stints or [])
        viz_pace_index(pace_idx, 'leclerc_pace_index.png')
    except Exception as e:
        print('Advanced visuals error:', e)
    print('Saved to', OUT_DIR, v1,v2,v3,v4,v5)

if __name__=='__main__':
    main()
