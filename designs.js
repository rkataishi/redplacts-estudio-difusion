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
  /* user background image */
  if(p.s.images.background){
   var opacity=Math.max(.28,(p.s.options.bgOpacity||32)/100);
   await api.coverImage(ctx,p.s.images.background,0,0,w,h,null,0,opacity);
  }
  /* top-left translucent veil for header readability */
  var vg=ctx.createLinearGradient(0,0,0,Math.round(h*.48));
  vg.addColorStop(0,'#f4f5f9dd');vg.addColorStop(1,'#f4f5f900');
  ctx.fillStyle=vg;ctx.fillRect(0,0,w,Math.round(h*.48));
  /* bottom veil so footer stands out */
  var vg2=ctx.createLinearGradient(0,h-260,0,h);
  vg2.addColorStop(0,'#f4f5f900');vg2.addColorStop(1,'#f4f5f9');
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
  /* left column: date + time + zone */
  var ly=y+16;
  api.drawText(ctx,api.textSpec(m.date.text||'',x,ly,m.leftW,m.date.size||31,700,api.C.ink,font),'m-date');
  ly+=m.date.h+9;
  api.drawText(ctx,api.textSpec(m.time.text||'',x,ly,m.leftW,m.time.size||28,400,api.C.ink,font),'m-time');
  ly+=m.time.h+6;
  api.drawText(ctx,api.textSpec(m.zone.text||'',x,ly,m.leftW,m.zone.size||18,400,api.C.muted,font),'m-zone');
  /* right column: platform + link + location */
  var ry=y+16,rx=x+m.rightX;
  api.drawText(ctx,api.textSpec(m.platform.text||'',rx,ry,m.rightX?w-m.rightX:w*.50,m.platform.size||21,700,api.C.ink,font),'m-platform');
  ry+=m.platform.h+8;
  api.drawText(ctx,api.textSpec(m.link.text||'',rx,ry,m.rightX?w-m.rightX:w*.50,m.link.size||19,400,api.C.muted,font),'m-link');
  ry+=m.link.h+8;
  if(m.location&&m.location.h)api.drawText(ctx,api.textSpec(m.location.text||'',rx,ry,m.rightX?w-m.rightX:w*.50,m.location.size||18,400,api.C.muted,font),'m-location');
  /* QR */
  if(m.qr)api.drawQR(ctx,m.qr,api.W-56-m.qrSize,y+16,m.qrSize);
 }

 /** Footer: redplacts.org + social handles */
 async function drawFooter(ctx,p){
  var y=p.footerTop||p.h-87;
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
  if(!p.valid){
   await drawFallback(ctx,p);
  } else {
   /* title block */
   drawTitleBlock(ctx,p);
   /* hero image */
   await drawHero(ctx,p);
   /* people grid */
   await drawPeopleGrid(ctx,p);
   /* moderators */
   await drawModerators(ctx,p);
   /* meeting band */
   drawMeetingBand(ctx,p);
  }

  /* 4. Footer — always present */
  await drawFooter(ctx,p);

  return {canvas:canvas,audit:audit};
 }

 window.RedPlactsDesigns={draw:draw};

 if(typeof module!=='undefined'&&module.exports)module.exports={draw:draw};
})();
