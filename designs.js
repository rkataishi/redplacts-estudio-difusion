/* designs.js — renderer de las nueve piezas con layouts por cantidad. */
(function(){
 'use strict';

 var api=null;

 var COMPOSITIONS=[
  {2:{id:'01-duo-fichas',kind:'duoCards'},3:{id:'01-tres-columnas',kind:'threeColumns'},4:{id:'01-reticula-dos-por-dos',kind:'grid'}},
  {2:{id:'02-duo-lateral',kind:'duoSide'},3:{id:'02-triada-central',kind:'centerTrio'},4:{id:'02-franja-cuatro',kind:'rowFour'}},
  {2:{id:'03-dos-columnas-editoriales',kind:'editorialDuo'},3:{id:'03-tres-columnas-editoriales',kind:'editorialColumns'},4:{id:'03-cuatro-retratos-a-sangre',kind:'fullBleedFour'}},
  {2:{id:'04-duo-diagonal',kind:'diagonalDuo'},3:{id:'04-triangulo-jerarquico',kind:'triangle'},4:{id:'04-mosaico-dos-por-dos',kind:'mosaic'}},
  {2:{id:'05-principal-y-acompanante',kind:'focusTwo'},3:{id:'05-principal-y-dos-secundarios',kind:'focusThree'},4:{id:'05-principal-y-tres-secundarios',kind:'focusFour'}},
  {2:{id:'06-dos-retratos-verticales',kind:'verticalTwo'},3:{id:'06-tres-columnas-verticales',kind:'verticalThree'},4:{id:'06-cuatro-bandas-fotograficas',kind:'verticalFour'}},
  {2:{id:'07-dos-tarjetas-amplias',kind:'digitalDuo'},3:{id:'07-tres-circulos-jerarquizados',kind:'circleTrio'},4:{id:'07-franja-horizontal-cuatro',kind:'digitalFour'}},
  {2:{id:'08-duo-desplazado',kind:'offsetDuo'},3:{id:'08-centro-y-satelites',kind:'satellites'},4:{id:'08-mosaico-dinamico',kind:'dynamicGrid'}},
  {2:{id:'09-titulo-y-dos-tarjetas',kind:'storyDuo'},3:{id:'09-tres-columnas-bajo-hero',kind:'storyTrio'},4:{id:'09-cuatro-retratos-superiores',kind:'storyFour'}}
 ];

 function recipe(v,n){
  if(COMPOSITIONS[v]&&COMPOSITIONS[v][n])return COMPOSITIONS[v][n];
  if(n<=1)return {id:String(v+1).padStart(2,'0')+'-retrato-individual',kind:'solo'};
  return {id:String(v+1).padStart(2,'0')+'-reticula-extendida',kind:'dense'};
 }

 function text(textValue,x,y,w,size,weight,color,font,align,leading){
  return api.textSpec(textValue||'',x,y,w,size,weight,color,font,align||'left',leading||1.12);
 }

 function fitted(textValue,x,y,w,maxH,maxSize,minSize,weight,color,font,align,leading){
  var value=textValue||'';
  for(var size=maxSize;size>=minSize;size-=2){
   var spec=text(value,x,y,w,size,weight,color,font,align,leading);
   if(spec.h<=maxH)return spec;
  }
  var fallback=text(value,x,y,w,minSize,weight,color,font,align,leading);
  fallback.overflow=fallback.h>maxH;
  return fallback;
 }

 function drawTracked(ctx,spec,label,audit){
  if(!spec||!spec.h)return;
  var before=audit.length;
  api.drawText(ctx,spec,label,audit);
  if(spec.overflow&&audit.length>before)audit[audit.length-1].overflow=true;
 }

 async function drawBackground(ctx,p){
  api.box(ctx,0,0,p.w,p.h,'#f7f7f6');
  if(p.s.images.background)await api.coverImage(ctx,p.s.images.background,0,0,p.w,p.h,null,0,Math.max(0,Math.min(.6,(p.s.options.bgOpacity??32)/100)));
  api.box(ctx,0,0,p.w,p.h,'rgba(255,255,255,.44)');
  await api.coverImage(ctx,{src:api.WAVE_ASSET},Math.round(p.w*.42),0,Math.round(p.w*.58),Math.round(p.h*.72),{x:52,y:45,zoom:1},0,.18);
 }

 async function drawHeader(ctx,p,audit){
  var h=p.v===1?118:128;
  api.box(ctx,0,0,p.w,h,'rgba(255,255,255,.94)');
  api.line(ctx,44,h-1,p.w-44,h-1,'#d8dce7');
  await api.containImage(ctx,api.BRAND_ASSETS[p.s.options.logo]||api.BRAND_ASSETS['logo-color'],44,15,150,h-27);
  var type=(p.s.event.type||'').toLocaleUpperCase('es');
  drawTracked(ctx,text(type,220,31,p.w-264,18,700,'#737bbd',p.font,'right'), 'event-type',audit);
  drawTracked(ctx,text('ENCUENTROS DE LA RED PLACTS',220,61,p.w-264,14,400,api.C.muted,p.font,'right'), 'event-series',audit);
 }

 function layoutGeometry(p,count){
  var w=p.w,h=p.h,footerTop=h-72,meetingH=p.v===1||p.v===3||p.v===7?126:p.v===5||p.v===8?174:150;
  var meetingY=footerTop-meetingH-14,modsH=p.s.moderators.length?(p.v===1&&p.s.moderators.length>1?150:72):0,modsY=meetingY-modsH-12,bottom=modsH?modsY-18:meetingY-18;
  var shrink=count===4?1:count===3?.55:0;
  var g={headerH:p.v===1?118:128,footerTop:footerTop,meetingY:meetingY,meetingH:meetingH,modsY:modsY,modsH:modsH};
  if(p.v===0){g.title={x:54,y:151,w:w-108,h:178};g.hero={x:54,y:345,w:w-108,h:278-54*shrink};g.people={x:54,y:g.hero.y+g.hero.h+26,w:w-108,h:bottom-(g.hero.y+g.hero.h+26)};}
  if(p.v===1){g.title={x:54,y:146,w:510,h:276};g.hero={x:600,y:143,w:w-654,h:292};g.people={x:54,y:466,w:w-108,h:bottom-466};}
  if(p.v===2){g.title={x:54,y:148,w:w-108,h:155};g.hero={x:54,y:315,w:w-108,h:205-35*shrink};g.people={x:54,y:g.hero.y+g.hero.h+24,w:w-108,h:bottom-(g.hero.y+g.hero.h+24)};}
  if(p.v===3){g.title={x:54,y:148,w:445,h:278};g.hero={x:526,y:146,w:500,h:286-30*shrink};g.people={x:54,y:454-22*shrink,w:w-108,h:bottom-(454-22*shrink)};}
  if(p.v===4){g.title={x:54,y:150,w:430,h:365};g.hero={x:510,y:148,w:516,h:382-32*shrink};g.people={x:54,y:558-22*shrink,w:w-108,h:bottom-(558-22*shrink)};}
  if(p.v===5){g.title={x:54,y:150,w:w-108,h:210};g.hero={x:54,y:380,w:w-108,h:470-80*shrink};g.people={x:54,y:g.hero.y+g.hero.h+30,w:w-108,h:bottom-(g.hero.y+g.hero.h+30)};}
  if(p.v===6){g.title={x:54,y:148,w:w-108,h:188};g.hero={x:54,y:348,w:w-108,h:245-40*shrink};g.people={x:54,y:g.hero.y+g.hero.h+26,w:w-108,h:bottom-(g.hero.y+g.hero.h+26)};}
  if(p.v===7){g.title={x:54,y:150,w:490,h:250};g.hero={x:0,y:128,w:w,h:380};g.people={x:54,y:526-25*shrink,w:w-108,h:bottom-(526-25*shrink)};g.overlayTitle=true;}
  if(p.v===8){g.title={x:54,y:525,w:w-108,h:235};g.hero={x:0,y:128,w:w,h:610};g.people={x:54,y:780-20*shrink,w:w-108,h:bottom-(780-20*shrink)};g.overlayTitle=true;}
  if(!p.s.images.hero){
   var titleH=p.v===5||p.v===8?250:p.v===1?190:210,peopleY=150+titleH+28;
   g.title={x:54,y:150,w:w-108,h:titleH};g.hero=null;g.overlayTitle=false;
   g.people={x:54,y:peopleY,w:w-108,h:bottom-peopleY};
  }
  return g;
 }

 function rect(x,y,w,h,mode){return {x:x,y:y,w:w,h:h,mode:mode||'top'};}
 function gridRects(cols,rows,gap){
  var out=[],cw=(1-gap*(cols-1))/cols,rh=(1-gap*(rows-1))/rows;
  for(var i=0;i<cols*rows;i++)out.push(rect((i%cols)*(cw+gap),Math.floor(i/cols)*(rh+gap),cw,rh,rows>1?'left':'top'));
  return out;
 }

 function peopleRects(kind,n){
  if(kind==='solo')return [rect(.20,0,.60,1,'cover')];
  if(kind==='duoCards')return [rect(0,0,.48,1,'left'),rect(.52,0,.48,1,'left')];
  if(kind==='threeColumns')return gridRects(3,1,.025);
  if(kind==='grid')return gridRects(2,2,.035);
  if(kind==='duoSide')return [rect(0,.06,.47,.88,'cover'),rect(.53,.06,.47,.88,'cover')];
  if(kind==='centerTrio')return [rect(0,.16,.29,.72,'top'),rect(.315,0,.37,1,'cover'),rect(.71,.16,.29,.72,'top')];
  if(kind==='rowFour')return gridRects(4,1,.02).map(function(r){r.mode='cover';return r;});
  if(kind==='editorialDuo')return [rect(0,0,.485,1,'cover'),rect(.515,0,.485,1,'cover')];
  if(kind==='editorialColumns')return gridRects(3,1,.025).map(function(r){r.mode='cover';return r;});
  if(kind==='fullBleedFour')return gridRects(4,1,.012).map(function(r){r.mode='cover';return r;});
  if(kind==='diagonalDuo')return [rect(0,0,.54,.76,'cover'),rect(.46,.24,.54,.76,'cover')];
  if(kind==='triangle')return [rect(0,.38,.31,.62,'top'),rect(.315,0,.37,.82,'cover'),rect(.69,.38,.31,.62,'top')];
  if(kind==='mosaic')return [rect(0,0,.48,.47,'left'),rect(.52,.05,.48,.42,'left'),rect(.04,.53,.44,.47,'left'),rect(.52,.50,.48,.50,'left')];
  if(kind==='focusTwo')return [rect(.38,0,.62,1,'cover'),rect(0,.20,.34,.60,'top')];
  if(kind==='focusThree')return [rect(.40,0,.60,1,'cover'),rect(0,0,.36,.47,'left'),rect(0,.53,.36,.47,'left')];
  if(kind==='focusFour')return [rect(.43,0,.57,1,'cover'),rect(0,0,.39,.30,'left'),rect(0,.35,.39,.30,'left'),rect(0,.70,.39,.30,'left')];
  if(kind==='verticalTwo')return [rect(0,0,.485,1,'cover'),rect(.515,0,.485,1,'cover')];
  if(kind==='verticalThree')return gridRects(3,1,.025).map(function(r){r.mode='cover';return r;});
  if(kind==='verticalFour')return gridRects(4,1,.018).map(function(r){r.mode='cover';return r;});
  if(kind==='digitalDuo')return [rect(0,.08,.48,.84,'top'),rect(.52,.08,.48,.84,'top')];
  if(kind==='circleTrio')return [rect(0,.20,.29,.68,'circle'),rect(.315,0,.37,1,'circle'),rect(.71,.20,.29,.68,'circle')];
  if(kind==='digitalFour')return gridRects(4,1,.02);
  if(kind==='offsetDuo')return [rect(.02,0,.55,.72,'cover'),rect(.43,.28,.55,.72,'cover')];
  if(kind==='satellites')return [rect(.31,0,.38,.78,'circle'),rect(0,.36,.28,.60,'circle'),rect(.72,.36,.28,.60,'circle')];
  if(kind==='dynamicGrid')return [rect(0,0,.58,.48,'cover'),rect(.62,0,.38,.48,'left'),rect(0,.52,.38,.48,'left'),rect(.42,.52,.58,.48,'cover')];
  if(kind==='storyDuo')return [rect(0,0,.48,1,'cover'),rect(.52,0,.48,1,'cover')];
  if(kind==='storyTrio')return gridRects(3,1,.025).map(function(r){r.mode='cover';return r;});
  if(kind==='storyFour')return gridRects(4,1,.018).map(function(r){r.mode='cover';return r;});
  return gridRects(n>4?3:Math.max(1,n),Math.ceil(n/3),.025);
 }

 async function drawHero(ctx,p,g,audit){
  if(!g.hero||!p.s.images.hero)return;
  await api.coverImage(ctx,p.s.images.hero,g.hero.x,g.hero.y,g.hero.w,g.hero.h,null,12);
  audit.push({label:'hero-image',x:g.hero.x,y:g.hero.y,w:g.hero.w,h:g.hero.h,maxLine:0});
 }

 function drawTitle(ctx,p,g,audit){
  var a=g.title,pad=18,titleValue=p.v>=3&&(p.s.options.socialTitle||'').trim()?p.s.options.socialTitle:p.s.event.title;
  var subtitleValue=p.v>=3&&(p.s.options.socialSubtitle||'').trim()?p.s.options.socialSubtitle:p.s.event.subtitle;
  if(g.overlayTitle)api.box(ctx,a.x-pad,a.y-pad,a.w+pad*2,a.h+pad*2,'rgba(255,255,255,.92)',16);
  var max=p.v===5||p.v===8?72:p.v===1?56:64;
  var titleSpec=fitted(titleValue||'Título del evento',a.x,a.y,a.w,a.h*.58,max,p.v>=3?26:32,700,api.C.ink,p.font,p.v===2?'center':'left',1.04);
  drawTracked(ctx,titleSpec,'event-title',audit);
  var y=a.y+titleSpec.h+12;
  var sub=fitted(subtitleValue,a.x,y,a.w,Math.max(28,a.h*.20),Math.max(20,Math.round(titleSpec.size*.45)),18,400,api.C.muted,p.font,titleSpec.align,1.18);
  drawTracked(ctx,sub,'event-subtitle',audit);
  y+=sub.h+(sub.h?10:0);
  if(p.s.event.reinforcement&&(p.v<3||p.s.options.socialReinforcement)){
   var reinforcement=fitted(p.s.event.reinforcement,a.x,y,a.w,Math.max(26,a.y+a.h-y),20,16,400,api.C.muted,p.font,titleSpec.align,1.2);
   drawTracked(ctx,reinforcement,'event-reinforcement',audit);
  }
 }

 async function drawPerson(ctx,p,item,area,index,audit){
  var x=area.x+item.x*area.w,y=area.y+item.y*area.h,w=item.w*area.w,h=item.h*area.h,person=p.s.speakers[index];
  if(!person)return;
  api.box(ctx,x,y,w,h,'rgba(255,255,255,.94)',12);
  var social=p.v>=3,showPhoto=!social||p.s.options.socialPhotos,nameSize=Math.max(17,Math.min(social?27:29,w*.075));
  if(!showPhoto){
   drawTracked(ctx,fitted(person.name||'Nombre',x+16,y+h*.34,w-32,h*.32,nameSize+3,16,700,api.C.ink,p.font,'center',1.08),'speaker-name-'+index,audit);
   return;
  }
  if(item.mode==='left'){
   var photo=Math.min(h-16,w*.38);
   await api.drawAvatar(ctx,person,x+8,y+(h-photo)/2,photo,p.font,'rect');
   audit.push({label:'speaker-photo-'+index,x:x+8,y:y+(h-photo)/2,w:photo,h:photo,maxLine:0});
   var tx=x+photo+20,tw=w-photo-28;
   var name=fitted(person.name||'Nombre',tx,y+14,tw,h*.42,nameSize,16,700,api.C.ink,p.font,'left',1.08);
   drawTracked(ctx,name,'speaker-name-'+index,audit);
   if(!social){var bio=fitted(person.description,tx,y+20+name.h,tw,h-name.h-34,Math.max(14,nameSize*.68),12,400,api.C.muted,p.font,'left',1.16);drawTracked(ctx,bio,'speaker-description-'+index,audit);}
   return;
  }
  if(item.mode==='circle'){
   var circle=Math.min(w*.82,h*.64),cx=x+(w-circle)/2;
   await api.drawAvatar(ctx,person,cx,y,circle,p.font,'circle');
   audit.push({label:'speaker-photo-'+index,x:cx,y:y,w:circle,h:circle,maxLine:0});
   var circleName=fitted(person.name||'Nombre',x+6,y+circle+10,w-12,h-circle-12,nameSize,15,700,api.C.ink,p.font,'center',1.08);
   drawTracked(ctx,circleName,'speaker-name-'+index,audit);
   return;
  }
  var photoH=item.mode==='cover'?h*.72:h*(social?.58:.52);
  if(person.photo)await api.coverImage(ctx,person.photo,x,y,w,photoH,person.crop,10);
  else api.box(ctx,x,y,w,photoH,'#e5e8ef',10);
  audit.push({label:'speaker-photo-'+index,x:x,y:y,w:w,h:photoH,maxLine:0});
  var labelY=y+photoH,backH=h-photoH;
  api.box(ctx,x,labelY,w,backH,'rgba(255,255,255,.96)',0);
  var nameTop=labelY+9;
  var topName=fitted(person.name||'Nombre',x+10,nameTop,w-20,backH*(social?.82:.44),nameSize,14,700,api.C.ink,p.font,'left',1.06);
  drawTracked(ctx,topName,'speaker-name-'+index,audit);
  if(!social){var topBio=fitted(person.description,x+10,nameTop+topName.h+6,w-20,Math.max(12,backH-topName.h-20),Math.max(13,nameSize*.62),11,400,api.C.muted,p.font,'left',1.13);drawTracked(ctx,topBio,'speaker-description-'+index,audit);}
 }

 async function drawPeople(ctx,p,g,r,audit){
  var area=g.people,items=peopleRects(r.kind,p.s.speakers.length);
  drawTracked(ctx,text(p.s.speakers.length===1?'EXPONE':'EXPONEN',area.x,area.y-22,area.w,15,700,api.C.muted,p.font), 'speaker-label',audit);
  for(var i=0;i<items.length&&i<p.s.speakers.length;i++)await drawPerson(ctx,p,items[i],area,i,audit);
 }

 async function drawModeration(ctx,p,g,audit){
  if(!p.s.moderators.length)return;
  var y=g.modsY,x=54,w=p.w-108,each=w/p.s.moderators.length;
  api.box(ctx,x,y,w,g.modsH,'rgba(255,255,255,.92)',10);
  drawTracked(ctx,text(p.s.moderators.length===1?'MODERA':'MODERAN',x+10,y+9,w-20,13,700,api.C.muted,p.font), 'moderation-label',audit);
  if(p.v===1&&p.s.moderators.length>1){
   var rowH=(g.modsH-28)/p.s.moderators.length;
   for(var j=0;j<p.s.moderators.length;j++){
    var moderator=p.s.moderators[j],rowY=y+27+j*rowH;
    await api.drawAvatar(ctx,moderator,x+10,rowY,34,p.font,'circle');
    var modName=fitted(moderator.name||'Nombre',x+54,rowY,w-68,20,16,13,700,api.C.ink,p.font,'left',1.05);
    drawTracked(ctx,modName,'mod-name-'+j,audit);
    drawTracked(ctx,fitted(moderator.description,x+54,rowY+modName.h+2,w-68,rowH-modName.h-5,11,9,400,api.C.muted,p.font,'left',1.05),'mod-desc-'+j,audit);
   }
   return;
  }
  for(var i=0;i<p.s.moderators.length;i++){
   var person=p.s.moderators[i],px=x+i*each+10,photo=34;
   await api.drawAvatar(ctx,person,px,y+31,photo,p.font,'circle');
   drawTracked(ctx,fitted(person.name||'Nombre',px+44,y+33,each-58,31,17,13,700,api.C.ink,p.font,'left',1.05),'mod-name-'+i,audit);
  }
 }

 function dateLabel(s){
  if(!s.event.date)return 'Fecha por confirmar';
  var d=new Date(s.event.date+'T12:00:00');
  return new Intl.DateTimeFormat('es',{day:'2-digit',month:'long',year:'numeric'}).format(d);
 }

 function visibleURL(s){
  if((s.event.urlLabel||'').trim())return s.event.urlLabel.trim();
  try{var parsed=new URL(s.event.url),value=parsed.hostname.replace(/^www\./,'')+(parsed.pathname==='/'?'':parsed.pathname);return value.length>42?value.slice(0,41)+'…':value;}
  catch(_){return 'Enlace por confirmar';}
 }

 function drawMeeting(ctx,p,g,audit){
  var x=54,y=g.meetingY,w=p.w-108,h=g.meetingH,left=w*.48,rightX=x+w*.54,social=p.v>=3;
  var qr=api.getQR({options:{showQR:social?p.s.options.socialQR:p.s.options.showQR},event:p.s.event});
  var qrSize=qr?Math.min(92,h-28):0,rightW=w*.42-(qrSize?qrSize+14:0);
  api.box(ctx,x,y,w,h,'rgba(237,240,246,.96)',12);
  drawTracked(ctx,fitted(dateLabel(p.s),x+16,y+15,left-24,h*.30,25,17,700,api.C.ink,p.font),'meeting-date',audit);
  var timeValue=p.s.event.time?(p.s.event.time+(p.s.event.endTime?' – '+p.s.event.endTime:'')+' h'):'Horario por confirmar';
  drawTracked(ctx,text(timeValue,x+16,y+52,left-24,20,400,api.C.ink,p.font),'meeting-time',audit);
  drawTracked(ctx,text(p.s.event.timezone,x+16,y+79,left-24,14,400,api.C.muted,p.font),'meeting-zone',audit);
  drawTracked(ctx,fitted(p.s.event.platform,rightX,y+15,rightW,h*.24,19,14,700,api.C.ink,p.font),'meeting-platform',audit);
  var url=visibleURL(p.s);
  api.box(ctx,rightX-7,y+47,rightW,h>150?31:27,'#142536',8);
  drawTracked(ctx,fitted(url,rightX,y+53,rightW-7,24,15,11,700,'#fff',p.font),'meeting-link',audit);
  if(p.s.event.location)drawTracked(ctx,fitted(p.s.event.location,rightX,y+88,rightW,h-95,14,11,400,api.C.muted,p.font),'meeting-location',audit);
  if(qr){var qrX=x+w-qrSize-12,qrY=y+(h-qrSize)/2;api.drawQR(ctx,qr,qrX,qrY,qrSize);audit.push({label:'meeting-qr',x:qrX,y:qrY,w:qrSize,h:qrSize,maxLine:0});}
 }

 async function drawFooter(ctx,p,g,audit){
  var y=g.footerTop;
  api.box(ctx,0,y,p.w,p.h-y,'rgba(255,255,255,.96)');
  api.line(ctx,44,y,p.w-44,y,'#d4d9e5');
  drawTracked(ctx,text('redplacts.org',54,y+20,210,18,700,api.C.ink,p.font),'website',audit);
  var handles=['@redplacts','@PlactsRed','@RedPLACTS','@redplacts'],step=(p.w-310)/handles.length;
  for(var i=0;i<handles.length;i++)drawTracked(ctx,text(handles[i],290+i*step,y+22,step-10,13,400,api.C.muted,p.font),'social-'+i,audit);
 }

 async function draw(p,scale,apiInput){
  api=apiInput;
  var ref=api.newCanvas(p,scale),ctx=ref.ctx,audit=ref.audit,count=p.s.speakers.length,r=recipe(p.v,count),g=layoutGeometry(p,count);
  p.layoutName=r.id;p.composition=r.id;p.compact=1;
  await drawBackground(ctx,p);
  await drawHeader(ctx,p,audit);
  await drawHero(ctx,p,g,audit);
  drawTitle(ctx,p,g,audit);
  await drawPeople(ctx,p,g,r,audit);
  await drawModeration(ctx,p,g,audit);
  drawMeeting(ctx,p,g,audit);
  await drawFooter(ctx,p,g,audit);
  p.valid=!audit.some(function(item){return item.overflow||item.x<0||item.y<0||item.x+item.w>p.w+1||item.y+item.h>p.h+1||item.maxLine>item.w+1;});
  return {canvas:ref.canvas,audit:audit};
 }

 window.RedPlactsDesigns={draw:draw};
 if(typeof module!=='undefined'&&module.exports)module.exports={draw:draw};
})();
