/* designs.js — renderer visual versionado para los nueve outputs. */
(function(){
 'use strict';

 /* ------------------------------------------------------------------ */
 /*  Helpers                                                            */
 /* ------------------------------------------------------------------ */

 /** fitting text into width, returns best {text,size,weight,color,font,
  *  align,leading,lines,h,x,y,w} — scans down from max to min. */
 function fitText(text,x,y,maxW,minW,maxSize,minSize,weight,color,font,align,leading){
  var spec=null;
  for(var s=maxSize;s>=minSize;s-=2){
   var t={text:String(text),x:x,y:y,w:maxW,size:s,weight:weight,color:color,font:font,align:align,leading:leading,lines:[]};
   t.lines=api.wrapLines(text,t.w,t.size,t.weight,t.font);
   t.h=t.lines.length*t.size*t.leading;
   spec=t;
   if(t.h<=maxW)return t; /* enough vertical space assigned via maxW — heuristic */
  }
  return spec;
 }

 /* ---- internal ref to api, set once at call time ---- */
 var api=null;

 /* ------------------------------------------------------------------ */
 /*  Sections                                                           */
 /* ------------------------------------------------------------------ */

 /** Background: full canvas with image at configurable opacity + veil */
 async function drawBackground(ctx,p){
  var w=p.w,h=p.h;
  /* solid base */
  api.box(ctx,0,0,w,h,'#f4f5f9');
  /* wave decoration */
  await api.coverImage(ctx,{src:api.WAVE_ASSET},Math.round(w*.38),0,Math.round(w*.65),Math.round(h*.78),{x:55,y:46,zoom:1},0,.55);
  /* user background image — full bleed, at least .85 opacity */
  if(p.s.images.background){
   var opacity=Math.max(.85,(p.s.options.bgOpacity||85)/100);
   await api.coverImage(ctx,p.s.images.background,0,0,w,h,null,0,opacity);
  }
  /* global white veil reduced to .08 so image reads through everywhere */
  ctx.fillStyle='rgba(255,255,255,.08)';
  ctx.fillRect(0,0,w,h);
  /* header veil kept separately semitransparent for readability */
  var hg=ctx.createLinearGradient(0,0,0,130);
  hg.addColorStop(0,'rgba(255,255,255,.72)');hg.addColorStop(1,'rgba(255,255,255,0)');
  ctx.fillStyle=hg;ctx.fillRect(0,0,w,130);
  /* bottom veil so footer stands out */
  var vg2=ctx.createLinearGradient(0,h-260,0,h);
  vg2.addColorStop(0,'rgba(255,255,255,0)');vg2.addColorStop(1,'rgba(255,255,255,.85)');
  ctx.fillStyle=vg2;ctx.fillRect(0,h-260,w,260);
 }

 /** Header: translucent band + logo + event type label */
 async function drawHeader(ctx,p){
  var w=p.w,mx=56;
  /* translucent header strip */
  api.box(ctx,0,0,w,130,'#ffffffcc',0);
  /* logo top-left */
  var logo=api.BRAND_ASSETS[p.s.options.logo]||api.BRAND_ASSETS['logo-color'];
  await api.containImage(ctx,logo,mx,20,155,95);
  /* event type */
  var evType=(p.s.event.type||'').toLocaleUpperCase('es');
  if(evType)api.drawText(ctx,api.textSpec(evType,mx+178,28,500,19,700,'#737bbd',p.font),'event-type');
  /* series label */
  api.drawText(ctx,api.textSpec('ENCUENTROS DE LA RED PLACTS',mx+178,58,500,14,400,api.C.muted,p.font),'event-series');
  /* thin accent line */
  api.line(ctx,mx,128,w-mx,128,'#d4d9e5');
 }

 /** Title + subtitle + reinforcement block */
 function drawTitleBlock(ctx,p){
  if(!p.intro)return;
  var i=p.intro;
  var y=i.y||155;
  /* title */
  api.drawText(ctx,api.textSpec(p.s.event.title||'Título del evento',i.x||56,y,i.w||(p.w-112),i.title.size||54,700,api.C.ink,p.font,i.title.align||'left',1.06),'title');
  y+=i.title.h;
  if(p.intro.sub&&p.intro.sub.h){y+=14;api.drawText(ctx,api.textSpec(p.s.event.subtitle||'',i.x||56,y,i.w||(p.w-112),i.sub.size||27,400,api.C.muted,p.font,i.sub.align||'left',1.2),'subtitle');y+=p.intro.sub.h;}
  if(p.intro.reinforcement&&p.intro.reinforcement.h){y+=15;api.drawText(ctx,api.textSpec(p.s.event.reinforcement||'',i.x||56,y,i.w||(p.w-112),i.reinforcement.size||22,400,api.C.muted,p.font,i.reinforcement.align||'left',1.24),'reinforcement');}
 }

 /** Hero image (if any) */
 async function drawHero(ctx,p){
  if(p.hero&&p.s.images.hero)await api.coverImage(ctx,p.s.images.hero,p.hero.x,p.hero.y,p.hero.w,p.hero.h,null,10);
 }

 /** People grid: avatar + name + description for every speaker */
 async function drawPeopleGrid(ctx,p){
  if(!p.people||!p.people.items||!p.people.items.length)return;
  var pl=p.people,px=p.peopleX||56,py=p.peopleY||340,font=p.font;
  /* section label */
  var label=p.s.speakers.length===1?'EXPONE':'EXPONEN';
  api.drawText(ctx,api.textSpec(label,px,py-38,pl.columns?Math.round((p.w-112)/pl.columns):p.w-112,17,700,api.C.muted,font),'people-label');
  /* draw each profile */
  for(var idx=0;idx<pl.items.length;idx++){
   var item=pl.items[idx];
   var ix=px+item.x,iy=py+item.y;
   /* avatar */
   var photoY=item.vertical?iy:iy+(item.h-item.photo)/2;
   var photoX=item.vertical?ix+(item.w-item.photo)/2:ix;
   await api.drawAvatar(ctx,item.person,photoX,photoY,item.photo,font,item.shape);
   /* name */
   var nameY=item.vertical?iy+item.photo+15:iy+(item.h-item.textH)/2;
   var tx=ix+(item.vertical?0:item.photo+17);
   var tw=item.vertical?item.w:item.w-item.photo-17;
   api.drawText(ctx,api.textSpec(item.person.name||'Nombre del participante',tx,nameY,tw,item.nt.size||28,700,api.C.ink,font,item.vertical?'center':'left',1.13),'name-'+idx);
   /* description */
   if(item.dt&&item.dt.h){
    var descY=nameY+item.nt.h+9;
    api.drawText(ctx,api.textSpec(item.person.description||'',tx,descY,tw,item.dt.size||22,400,api.C.muted,font,item.vertical?'center':'left',1.24),'desc-'+idx);
   }
  }
 }

 /** Moderators row */
 async function drawModerators(ctx,p){
  if(!p.mods||!p.mods.items||!p.mods.items.length)return;
  var ml=p.mods,px=p.modsX||56,py=p.modsY||700,font=p.font,w=p.w-112;
  api.drawText(ctx,api.textSpec(ml.label||'MODERA',px,py,w,17,700,api.C.muted,font),'mod-label');
  for(var i=0;i<ml.items.length;i++){
   var it=ml.items[i];
   await api.drawAvatar(ctx,it.person,px+it.x,py+34,it.photo,font,'circle');
   api.drawText(ctx,api.textSpec(it.person.name||'Nombre',px+it.x+it.photo+16,py+34,it.w-it.photo-16,it.nt.size||24,700,api.C.ink,font),'mod-name-'+i);
   if(it.dt&&it.dt.h)api.drawText(ctx,api.textSpec(it.person.description||'',px+it.x+it.photo+16,py+34+it.nt.h+7,it.w-it.photo-16,it.dt.size||20,400,api.C.muted,font),'mod-desc-'+i);
  }
 }

 /** Meeting band: date, time, timezone, platform, link, location */
  function drawMeetingBand(ctx,p){
   if(!p.meeting)return;
   var m=p.meeting,x=56,y=p.metaY||p.h-220,w=m.width||(p.w-112),font=p.font;
   api.box(ctx,x-18,y-8,w+36,m.h+16,'#edf0f6',12);
   /* left column: date + time + zone — accept both poster & social keys */
   var date=m.date||m.d,time=m.time||m.t,zone=m.zone||m.z;
   var ly=y+16;
   if(date)api.drawText(ctx,api.textSpec(date.text||'',x,ly,m.leftW,date.size||31,700,api.C.ink,font),'m-date');
   ly+=(date&&date.h?date.h:0)+9;
   if(time)api.drawText(ctx,api.textSpec(time.text||'',x,ly,m.leftW,time.size||28,400,api.C.ink,font),'m-time');
   ly+=(time&&time.h?time.h:0)+6;
   if(zone)api.drawText(ctx,api.textSpec(zone.text||'',x,ly,m.leftW,zone.size||18,400,api.C.muted,font),'m-zone');
  /* right column: platform + link + location */
  var ry=y+16,rx=x+m.rightX;
  api.drawText(ctx,api.textSpec(m.platform.text||'',rx,ry,m.rightX?w-m.rightX:w*.50,m.platform.size||21,700,api.C.ink,font),'m-platform');
  ry+=m.platform.h+8;
  api.drawText(ctx,api.textSpec(m.link.text||'',rx,ry,m.rightX?w-m.rightX:w*.50,m.link.size||19,400,api.C.muted,font),'m-link');
  ry+=m.link.h+8;
  if(m.location&&m.location.h)api.drawText(ctx,api.textSpec(m.location.text||'',rx,ry,m.rightX?w-m.rightX:w*.50,m.location.size||18,400,api.C.muted,font),'m-location');
  /* QR */
  if(m.qr)api.drawQR(ctx,m.qr,p.w-56-m.qrSize,y+16,m.qrSize);
 }

 /** Footer: redplacts.org + social handles */
 async function drawFooter(ctx,p){
  var y=p.footerTop||p.h-87;
  /* opaque white footer background for readability */
  api.box(ctx,0,y,p.w,p.h-y,'rgba(255,255,255,0.94)',0);
  api.line(ctx,56,y,p.w-56,y,'#d4d9e5');
  api.drawText(ctx,api.textSpec('redplacts.org',56,y+18,218,23,700,api.C.ink,p.font),'website');
  var nx=293;
  var networks=[{handle:'@redplacts',icon:'instagram'},{handle:'@PlactsRed',icon:'x'},{handle:'@RedPLACTS',icon:'youtube'},{handle:'@redplacts',icon:'facebook'}];
  for(var i=0;i<networks.length;i++){
   var n=networks[i];
   try{await api.drawIcon(ctx,n.icon,nx,y+34,19,api.C.muted);}catch(_){}
   api.drawText(ctx,api.textSpec(n.handle,nx+27,y+32,149,17,400,api.C.muted,p.font),'social-'+i);
   nx+=184;
  }
 }

 /** Fallback for when p.valid === false — still show header + background */
 async function drawFallback(ctx,p){
  api.box(ctx,0,0,p.w,p.h,'#f4f5f9');
  await api.containImage(ctx,api.BRAND_ASSETS['logo-color'],Math.round(p.w/2-108),Math.round(p.h/2-180),216,165);
  api.drawText(ctx,api.textSpec('Este contenido necesita\nmás espacio.',Math.round(p.w*.1),Math.round(p.h*.38),Math.round(p.w*.8),56,700,api.C.ink,p.font,'center'),'fallback-title');
  api.drawText(ctx,api.textSpec('Abrevia los textos o elige un formato más alto. No se estira el lienzo ni se recorta contenido.',Math.round(p.w*.12),Math.round(p.h*.54),Math.round(p.w*.76),28,400,api.C.muted,p.font,'center',1.4),'fallback-hint');
 }

 /* ------------------------------------------------------------------ */
 /*  v0 — Institutional layout with fixed portrait zones                */
 /* ------------------------------------------------------------------ */

 function applyV0Layout(p){
  /* Fixed dimensions for institutional poster (1080×1350 class) */
  var W=p.w, H=p.h, MX=56;
  var contentW=W-MX*2;

  /* Intro block: title + subtitle + reinforcement */
  p.intro={
   x:MX, y:155, w:contentW,
   title:{size:52},
   sub:{size:26},
   reinforcement:{size:21}
  };

  /* Hero occupies centre band when present */
  p.hero={x:MX, y:260, w:contentW, h:260};

  /* People: bounded compact portrait grid — cols by count, fixed photo caps */
  var sp=p.s.speakers||[];
  var n=sp.length;
  var cols=n<=1?1:n===2?2:3;
  var gap=30;
  var photoSide=cols===1?180:cols===2?120:84;
  var rowH=125;                                /* hard cap */
  var startY=550;

  var colW=Math.round((contentW-gap*(cols-1))/cols);
  var textW=colW-photoSide-18;
  var items=[];
  for(var i=0;i<n;i++){
   var col=i%cols, row=Math.floor(i/cols);
   var ix=col*(colW+gap);
   var iy=row*(rowH+18);
   var nt=api.wrapLines(sp[i].name||'',textW,28,700,p.font);
   var dt=api.wrapLines(sp[i].description||'',textW,20,400,p.font);
   var ntH=nt.length*28*1.13;
   var dtH=dt.length*20*1.24;
   items.push({
    x:ix, y:iy, w:colW, h:rowH,
    person:sp[i], photo:photoSide,
    shape:'rect', vertical:false,
    nt:{size:28,h:ntH,lines:nt},
    dt:{size:20,h:dtH,lines:dt}
   });
  }
  p.people={
   items:items, columns:cols,
   columnW:colW, rowH:rowH
  };
  p.peopleX=MX; p.peopleY=startY;

  /* Moderators: start capped at 900, fixed photo 56 */
  var mods=p.s.moderators||[];
  var modStartY=Math.min(900, startY+Math.ceil(n/cols)*(rowH+18)+30);
  var modPhoto=56;
  var modItems=[];
  var modColW=mods.length?Math.round((contentW-gap*Math.max(mods.length-1,0))/mods.length):0;
  for(var j=0;j<mods.length;j++){
   var mTextW=modColW-modPhoto-16;
   var mNt=api.wrapLines(mods[j].name||'',mTextW,24,700,p.font);
   var mDt=api.wrapLines(mods[j].description||'',mTextW,20,400,p.font);
   modItems.push({
    x:j*(modColW+gap), photo:modPhoto,
    w:modColW, person:mods[j],
    nt:{size:24,h:mNt.length*24*1.13,lines:mNt},
    dt:{size:20,h:mDt.length*20*1.24,lines:mDt}
   });
  }
  p.mods={
   items:modItems,
   label:mods.length===1?'MODERA':'MODERAN'
  };
  p.modsX=MX; p.modsY=modStartY;

  /* Meeting band: y1010 or H-260 (whichever is smaller), h220, preserve content */
  var mbH=220;
  p.metaY=Math.min(1010,H-260);
  p.meeting={...p.meeting, width:contentW, h:mbH};
  p.footerTop=H-87;
 }

 /* ------------------------------------------------------------------ */
 /*  v1 — True landscape 1350×1080 layout                              */
 /* ------------------------------------------------------------------ */

 function applyV1Layout(p){
  var W=1350, H=1080, MX=56;

  /* Title block: left column x56..620, y150 */
  p.intro={
   x:MX, y:150, w:564,
   title:{size:52},
   sub:{size:26},
   reinforcement:{size:21}
  };

  /* Hero image: right column x690 y145, 604×380 */
  p.hero={x:690, y:145, w:604, h:380};

  /* Speakers lower strip: x56 y560, w900 */
  var sp=p.s.speakers||[];
  var cols=sp.length<=3?3:sp.length<=6?3:4;
  var gap=20;
  var stripW=900;
  var colW=Math.round((stripW-gap*(cols-1))/cols);
  var photoSide=Math.round(colW*.38);
  var textW=colW-photoSide-14;
  var rowH=photoSide+24;
  var items=[];
  for(var i=0;i<sp.length;i++){
   var col=i%cols, row=Math.floor(i/cols);
   var ix=col*(colW+gap);
   var iy=row*(rowH+16);
   var nt=api.wrapLines(sp[i].name||'',textW,24,700,p.font);
   var dt=api.wrapLines(sp[i].description||'',textW,17,400,p.font);
   items.push({
    x:ix, y:iy, w:colW, h:rowH,
    person:sp[i], photo:photoSide,
    shape:'rect', vertical:false,
    nt:{size:24,h:nt.length*24*1.13,lines:nt},
    dt:{size:17,h:dt.length*17*1.24,lines:dt}
   });
  }
  p.people={items:items, columns:cols, columnW:colW, rowH:rowH};
  p.peopleX=MX; p.peopleY=560;

  /* Moderators right: x980, below hero */
  var mods=p.s.moderators||[];
  var modItems=[];
  var modW=W-MX-980; /* ~314 */
  var modGap=16;
  for(var j=0;j<mods.length;j++){
   var mPhoto=Math.round(modW*.35);
   var mTextW=modW-mPhoto-12;
   var mNt=api.wrapLines(mods[j].name||'',mTextW,20,700,p.font);
   var mDt=api.wrapLines(mods[j].description||'',mTextW,16,400,p.font);
   modItems.push({
    x:0, y:j*(rowH+modGap), photo:mPhoto,
    w:modW, person:mods[j],
    nt:{size:20,h:mNt.length*20*1.13,lines:mNt},
    dt:{size:16,h:mDt.length*16*1.24,lines:mDt}
   });
  }
  p.mods={items:modItems, label:mods.length===1?'MODERA':'MODERAN'};
  p.modsX=980; p.modsY=545;

  /* Meeting band: bottom — merge layout sizing into incoming meeting */
   var mH=(p.meeting&&p.meeting.h)||115;
   p.metaY=Math.min(H-200,H-mH-8);
   p.meeting={
    ...p.meeting,
    width:W-MX*2, h:mH,
    date:{...(p.meeting||{}).date,size:31},
    time:{...(p.meeting||{}).time,size:28},
    zone:{...(p.meeting||{}).zone,size:18},
    platform:{...(p.meeting||{}).platform,size:21},
    link:{...(p.meeting||{}).link,size:19},
    location:{...(p.meeting||{}).location,size:18}
   };
  p.footerTop=H-75;
 }

 /* ------------------------------------------------------------------ */
 /*  v2 — Editorial portrait 1080×1350: full-width title, wide hero,    */
 /*       rectangular profile grid and separated moderation             */
 /* ------------------------------------------------------------------ */

 function applyV2Layout(p){
  var W=p.w, H=p.h, MX=56;
  var contentW=W-MX*2;
  var footerTop=H-87;

  /* Full-width title, fitted so the hero keeps its fixed band at y=380 */
  var titleTop=150, titleSpace=222;
  var intro=null, titleFits=false;
  for(var ts=54; ts>=36; ts-=2){
   var t=api.textSpec(p.s.event.title||'Título del evento',MX,titleTop,contentW,ts,700,api.C.ink,p.font,'left',1.06);
   var s=api.textSpec(p.s.event.subtitle||'',MX,0,contentW,Math.max(22,Math.round(ts*.5)),400,api.C.muted,p.font,'left',1.2);
   var r=api.textSpec(p.s.event.reinforcement||'',MX,0,contentW,Math.max(18,Math.round(ts*.4)),400,api.C.muted,p.font,'left',1.24);
   var introH=t.h+(s.h?14+s.h:0)+(r.h?15+r.h:0);
   intro={x:MX,y:titleTop,w:contentW,title:t,sub:s,reinforcement:r};
   if(introH<=titleSpace){titleFits=true;break;}
  }
  p.intro=intro;

  /* Wide hero banner across the page */
  p.hero={x:MX,y:380,w:contentW,h:300};

  /* People: rectangular profiles in a grid that starts below the hero */
  var sp=p.s.speakers||[];
  var n=sp.length;
  var cols=n<=1?1:n===2?2:3;
  var gap=24, rowGap=14;
  var colW=Math.round((contentW-gap*(cols-1))/cols);

  /* Moderators: separate compact band above the meeting strip */
  var mods=p.s.moderators||[];
  var modGap=24;
  var modColW=mods.length?Math.round((contentW-modGap*(mods.length-1))/mods.length):0;
  var modPhoto=56, modNameSize=22;
  var modItems=[], modBlockH=0;
  for(var j=0;j<mods.length;j++){
   var mtw=modColW-modPhoto-16;
   var mnt=api.textSpec(mods[j].name||'Nombre de moderación',0,0,mtw,modNameSize,700,api.C.ink,p.font,'left',1.12);
   var mdt=api.textSpec(mods[j].description||'',0,0,mtw,17,400,api.C.muted,p.font,'left',1.24);
   modBlockH=Math.max(modBlockH,Math.max(modPhoto,mnt.h+(mdt.h?7+mdt.h:0)));
   modItems.push({x:j*(modColW+modGap),photo:modPhoto,w:modColW,person:mods[j],nt:{size:modNameSize,h:mnt.h,lines:mnt.lines},dt:{size:17,h:mdt.h,lines:mdt.lines}});
  }
  var modsH=mods.length?34+modBlockH:0;

  /* Meeting band pinned above the footer */
  var meeting=p.meeting||{h:120};
  var metaY=footerTop-22-meeting.h;
  p.meeting=meeting;
  p.metaY=metaY;
  p.footerTop=footerTop;

  var modsY=mods.length?metaY-24-modsH:metaY-24;
  p.mods={items:modItems,label:mods.length===1?'MODERA':'MODERAN'};
  p.modsX=MX; p.modsY=modsY;

  /* Profile grid: fit rectangular photos inside the free band */
  var peopleStart=724;
  var peopleEnd=mods.length?modsY-22:metaY-24;
  var peopleSpace=peopleEnd-peopleStart;
  var rows=Math.max(1,Math.ceil(n/cols));
  var maxRowH=(peopleSpace-(rows-1)*rowGap)/rows;
  var desiredPhoto=cols===1?200:cols===2?176:125;
  var photoH=Math.max(56,Math.round(Math.min(desiredPhoto,maxRowH)));
  var textW=colW-photoH-17;
  var nameSize=cols===1?34:cols===2?26:22;
  var descSize=cols===1?21:cols===2?18:15;
  var profiles=[], rowH=photoH;
  for(var i=0;i<n;i++){
   var nt=api.textSpec(sp[i].name||'Nombre del participante',0,0,textW,nameSize,700,api.C.ink,p.font,'left',1.13);
   var dt=api.textSpec(sp[i].description||'',0,0,textW,descSize,400,api.C.muted,p.font,'left',1.24);
   var textH=nt.h+(dt.h?9+dt.h:0);
   rowH=Math.max(rowH,textH);
   profiles.push({person:sp[i],col:i%cols,row:Math.floor(i/cols),nt:nt,dt:dt,textH:textH});
  }
  var items=profiles.map(function(it){
   return {x:it.col*(colW+gap),y:it.row*(rowH+rowGap),w:colW,h:rowH,person:it.person,photo:photoH,shape:'rect',vertical:false,textH:it.textH,nt:{size:nameSize,h:it.nt.h,lines:it.nt.lines},dt:{size:descSize,h:it.dt.h,lines:it.dt.lines}};
  });
  var peopleH=rows*rowH+(rows-1)*rowGap;
  p.people={items:items,columns:cols,columnW:colW,rowH:rowH,rows:rows};
  p.peopleX=MX; p.peopleY=peopleStart;

  p.valid=titleFits&&peopleH<=peopleSpace&&maxRowH>=56;
 }

 /* ------------------------------------------------------------------ */
 /*  Main draw entry point                                              */
 /* ------------------------------------------------------------------ */

 async function draw(p, scale, apiInput){
  api=apiInput;
  var ref=api.newCanvas(p,scale);
  var canvas=ref.canvas,ctx=ref.ctx,audit=ref.audit;

  /* 1. Full background with image + veil */
  await drawBackground(ctx,p);

  /* 2. Header: translucent + logo */
  await drawHeader(ctx,p);

  /* 3. Content: fallback or full layout */
  if(p.v===2){
   /* v2 editorial portrait: full-width title, wide hero, profile grid */
   applyV2Layout(p);
   if(p.valid){
    drawTitleBlock(ctx,p);
    await drawHero(ctx,p);
    await drawPeopleGrid(ctx,p);
    await drawModerators(ctx,p);
    drawMeetingBand(ctx,p);
   } else {
    await drawFallback(ctx,p);
   }
   } else if(!p.valid){
   await drawFallback(ctx,p);
   } else if(p.v===0){
    /* v0 institutional layout: fixed portrait zones */
    applyV0Layout(p);
    drawTitleBlock(ctx,p);
    await drawHero(ctx,p);
    await drawPeopleGrid(ctx,p);
    await drawModerators(ctx,p);
    drawMeetingBand(ctx,p);
   } else if(p.v===1){
    /* v1 true landscape 1350×1080 */
    applyV1Layout(p);
    drawTitleBlock(ctx,p);
    await drawHero(ctx,p);
    await drawPeopleGrid(ctx,p);
    await drawModerators(ctx,p);
    drawMeetingBand(ctx,p);
   } else {
    /* social v>=3: hero differentiated from background — Sol spec */
    if(p.s.images.hero){
     if(p.v===3) p.hero={x:p.w-424,y:145,w:368,h:260};
     else if(p.v===4) p.hero={x:p.w-424,y:145,w:368,h:300};
     else if(p.v===6) p.hero={x:p.w-424,y:145,w:368,h:300};
     else if(p.v===5) p.hero={x:56,y:820,w:p.w-112,h:360};
     else if(p.v===7) p.hero={x:0,y:0,w:p.w,h:560};
     else if(p.v===8) p.hero={x:0,y:0,w:p.w,h:Math.round(p.h*.62)};
     else if(!p.hero){
      p.hero=p.story
       ?{x:0,y:0,w:p.w,h:Math.round(p.h*.52)}
       :{x:0,y:Math.round(p.h*.68),w:p.w,h:Math.round(p.h*.25)};
     }
    } else {
     /* no hero image: keep Digital family full-bleed placeholders if needed */
     if(p.v===7) p.hero={x:0,y:0,w:p.w,h:560};
     else if(p.v===8) p.hero={x:0,y:0,w:p.w,h:Math.round(p.h*.62)};
    }
    if(p.intro&&(p.v===3||p.v===4||p.v===6)) p.intro.w=500;
     /* recompute title size so it fits panel: max 64px, max 3 lines */
     if(p.intro&&(p.v===3||p.v===4||p.v===6)){
      var _max=64,_min=32,_cap=3;
      for(var _ts2=_max;_ts2>=_min;_ts2-=2){
       var _ln=api.wrapLines(p.s.event.title||'Título del evento',p.intro.w,_ts2,700,p.font);
       if(_ln.length<=_cap){p.intro.title.size=_ts2;p.intro.title.h=_ln.length*_ts2*1.06;p.intro.title.lines=_ln;break;}
      }
     }
     /* v5: hero at y820, title must end before hero — max 76px, max 3 lines */
     if(p.v===5&&p.intro){
      var _max5=76,_min5=32,_cap5=3;
      for(var _ts5=_max5;_ts5>=_min5;_ts5-=2){
       var _ln5=api.wrapLines(p.s.event.title||'Título del evento',p.intro.w||p.w-112,_ts5,700,p.font);
       if(_ln5.length<=_cap5){p.intro.title.size=_ts5;p.intro.title.h=_ln5.length*_ts5*1.06;p.intro.title.lines=_ln5;break;}
      }
     }
     /* draw hero before title so text overlays the image */
     await drawHero(ctx,p);
     await drawHeader(ctx,p); /* redraw so header/logo sit above hero */
      /* white title backing panel — generic branch */
      if(p.v===3||p.v===4||p.v===6) api.box(ctx,40,120,540,330,'rgba(255,255,255,0.94)',18);
      else if(p.v===5)api.box(ctx,40,470,p.w-80,300,'rgba(255,255,255,0.94)',18);
      else if(p.v===7)api.box(ctx,40,110,p.w-80,340,'rgba(255,255,255,0.94)',18);
      else if(p.v===8)api.box(ctx,40,450,p.w-80,430,'rgba(255,255,255,0.94)',18);
     drawTitleBlock(ctx,p);
    /* white translucent panel for names readability */
     if(p.namesY&&p.names&&p.names.h){
      api.box(ctx,56,p.namesY-8,p.w-112,p.names.h+16,'rgba(255,255,255,0.94)',18);
     }
   if(api.drawSocialNames){
     await api.drawSocialNames(ctx,p,audit);
    } else {
     await drawPeopleGrid(ctx,p);
     await drawModerators(ctx,p);
    }
    if(api.drawSocialMeeting){
     api.drawSocialMeeting(ctx,p,audit);
    } else {
     drawMeetingBand(ctx,p);
    }
  }

  /* 4. Footer — always present */
  await drawFooter(ctx,p);

  return {canvas:canvas,audit:audit};
 }

 window.RedPlactsDesigns={draw:draw};

 if(typeof module!=='undefined'&&module.exports)module.exports={draw:draw};
})();
