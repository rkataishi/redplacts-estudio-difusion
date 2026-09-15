(function(){
 'use strict';

 var api=null;

 var COMPOSITIONS=[
  {2:{id:'01-duo-fichas',kind:'duoCards'},3:{id:'01-tres-columnas',kind:'threeColumns'},4:{id:'01-reticula-dos-por-dos',kind:'grid'}},
  {2:{id:'02-duo-lateral-igual',kind:'duoSide'},3:{id:'02-tres-panoramicas-iguales',kind:'panoramaTrio'},4:{id:'02-franja-cuatro-iguales',kind:'rowFour'}},
  {2:{id:'03-dos-columnas-editoriales',kind:'editorialDuo'},3:{id:'03-tres-columnas-editoriales',kind:'editorialColumns'},4:{id:'03-cuatro-retratos-a-sangre',kind:'fullBleedFour'}},
  {2:{id:'04-duo-alineado',kind:'squareDuo'},3:{id:'04-tres-alineados',kind:'squareTrio'},4:{id:'04-reticula-dos-por-dos',kind:'squareGrid'}},
  {2:{id:'05-duo-editorial-alineado',kind:'publicationDuo'},3:{id:'05-tres-editoriales-alineados',kind:'publicationTrio'},4:{id:'05-reticula-editorial',kind:'publicationGrid'}},
  {2:{id:'06-dos-retratos-verticales',kind:'verticalTwo'},3:{id:'06-tres-columnas-verticales',kind:'verticalThree'},4:{id:'06-cuatro-bandas-fotograficas',kind:'verticalFour'}},
  {2:{id:'07-dos-tarjetas-iguales',kind:'digitalDuo'},3:{id:'07-tres-circulos-iguales',kind:'circleTrio'},4:{id:'07-franja-cuatro-iguales',kind:'digitalFour'}},
  {2:{id:'08-duo-modular-alineado',kind:'digitalSquareDuo'},3:{id:'08-tres-modulares-alineados',kind:'digitalSquareTrio'},4:{id:'08-reticula-modular',kind:'digitalSquareGrid'}},
  {2:{id:'09-dos-bandas-horizontales',kind:'storyRowsTwo'},3:{id:'09-tres-bandas-horizontales',kind:'storyRowsThree'},4:{id:'09-reticula-horizontal-dos-por-dos',kind:'storyGridFour'}}
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

 function boxSettings(p,key){
  var boxes=p.s.options.boxes||{},value=boxes[key]||{};
  return {style:value.style||'transparent',color:value.color||'default',accent:value.accent||'#0062ad',fontScale:Number(value.fontScale)||100};
 }

 function typeSize(p,key,size){
  var globalScale=(Number(p.s.options.typeScale)||115)/100,localScale=key?boxSettings(p,key).fontScale/100:1;
  return Math.max(17,Math.round(size*globalScale*localScale));
 }

 function typed(p,key,textValue,x,y,w,size,weight,color,font,align,leading){
  return text(textValue,x,y,w,typeSize(p,key,size),weight,color,font,align,leading);
 }

 function fittedType(p,key,textValue,x,y,w,maxH,maxSize,minSize,weight,color,font,align,leading){
  var max=typeSize(p,key,maxSize),min=typeSize(p,null,minSize);
  return fitted(textValue,x,y,w,maxH,Math.max(max,min),min,weight,color,font,align,leading);
 }

 function alpha(hex,opacity){
  var value=(hex||'#ffffff').replace('#','');
  if(value.length===3)value=value.split('').map(function(char){return char+char;}).join('');
  return 'rgba('+parseInt(value.slice(0,2),16)+','+parseInt(value.slice(2,4),16)+','+parseInt(value.slice(4,6),16)+','+opacity+')';
 }

 function boxTheme(ctx,p,key,x,w){
  var settings=boxSettings(p,key),base=settings.color==='dark'?'#142536':settings.color==='accent'?settings.accent:'#ffffff';
  var fill=settings.style==='vibrant'?alpha(base,.96):alpha(base,settings.color==='default'?.76:.62);
  if(settings.style==='gradient'){
   fill=ctx.createLinearGradient(x,0,x+w,0);
   fill.addColorStop(0,alpha(base,.96));
   fill.addColorStop(1,alpha(base,settings.color==='default'?.38:.28));
  }
  return {fill:fill,text:settings.color==='default'?api.C.ink:'#ffffff',muted:settings.color==='default'?api.C.muted:'rgba(255,255,255,.78)'};
 }

 function drawTracked(ctx,spec,label,audit){
  if(!spec||!spec.h)return;
  var before=audit.length;
  api.drawText(ctx,spec,label,audit);
  if(spec.overflow&&audit.length>before)audit[audit.length-1].overflow=true;
 }

 function drawStack(ctx,items,top,height,gap,audit){
  var visible=items.filter(function(item){return item.spec&&item.spec.h;});
  var total=visible.reduce(function(sum,item){return sum+item.spec.h;},0)+Math.max(0,visible.length-1)*gap;
  var y=top+Math.max(0,(height-total)/2);
  visible.forEach(function(item){item.spec.y=y;drawTracked(ctx,item.spec,item.label,audit);y+=item.spec.h+gap;});
 }

 async function drawBackground(ctx,p){
  api.box(ctx,0,0,p.w,p.h,'#f7f7f6');
  if(p.s.images.background)await api.coverImage(ctx,p.s.images.background,0,0,p.w,p.h,null,0,Math.max(0,Math.min(.6,(p.s.options.bgOpacity??32)/100)));
  api.box(ctx,0,0,p.w,p.h,'rgba(255,255,255,.44)');
  await api.coverImage(ctx,{src:api.WAVE_ASSET},Math.round(p.w*.42),0,Math.round(p.w*.58),Math.round(p.h*.72),{x:52,y:45,zoom:1},0,.18);
 }

 async function drawHeader(ctx,p,audit){
  var h=p.v===1?118:128;
  ctx.save();ctx.shadowColor='#14253645';ctx.shadowBlur=18;ctx.shadowOffsetY=8;api.box(ctx,0,0,p.w,h,'rgba(255,255,255,.94)');ctx.restore();
  api.line(ctx,44,h-1,p.w-44,h-1,'#d8dce7');
  await api.containImage(ctx,api.BRAND_ASSETS[p.s.options.logo]||api.BRAND_ASSETS['logo-color'],44,15,150,h-27);
  var type=(p.s.event.type||'').toLocaleUpperCase('es'),right=220,width=p.w-264;
  drawStack(ctx,[
   {spec:typed(p,null,type,right,0,width,23,700,'#737bbd',p.font,'right'),label:'event-type'},
   {spec:typed(p,null,'ENCUENTROS VIRTUALES DE LA RED PLACTS',right,0,width,17,400,api.C.muted,p.font,'right'),label:'event-series'}
  ],14,h-28,7,audit);
 }

 function layoutGeometry(p,count){
  var w=p.w,h=p.h,footerTop=h-104,meetingH=p.v===1||p.v===3||p.v===7?138:p.v===5||p.v===8?174:158;
  var modsH=p.s.moderators.length?Math.max(p.v===6?140:128,...p.s.moderators.map(function(person){var tw=(w-108)/p.s.moderators.length-112;return 62+typed(p,'moderator',person.name,0,0,tw,18,700,api.C.ink,p.font).h+typed(p,'moderator',person.affiliation,0,0,tw,16,400,api.C.muted,p.font).h;})):0;
  var meetingY=footerTop-meetingH-14,modsY=meetingY-modsH-24,bottom=modsH?modsY-24:meetingY-24;
  var shrink=count===4?1:count===3?.55:0;
  var g={headerH:p.v===1?118:128,footerTop:footerTop,meetingY:meetingY,meetingH:meetingH,modsY:modsY,modsH:modsH};
  if(p.v===0){g.title={x:54,y:151,w:w-108,h:178};g.hero={x:54,y:345,w:w-108,h:278-54*shrink};g.people={x:54,y:g.hero.y+g.hero.h+26,w:w-108,h:bottom-(g.hero.y+g.hero.h+26)};}
  if(p.v===1){g.title={x:54,y:146,w:510,h:276};g.hero={x:600,y:143,w:w-654,h:292};var peopleY=count===4?448:466;g.people={x:54,y:peopleY,w:w-108,h:bottom-peopleY};}
  if(p.v===2){g.title={x:54,y:148,w:w-108,h:155};g.hero={x:54,y:315,w:w-108,h:205-35*shrink};g.people={x:54,y:g.hero.y+g.hero.h+24,w:w-108,h:bottom-(g.hero.y+g.hero.h+24)};}
  if(p.v===3){g.title={x:54,y:148,w:445,h:278};g.hero={x:526,y:146,w:500,h:286-30*shrink};g.people={x:54,y:454-22*shrink,w:w-108,h:bottom-(454-22*shrink)};}
  if(p.v===4){g.title={x:54,y:150,w:430,h:365};g.hero={x:510,y:148,w:516,h:382-32*shrink};g.people={x:54,y:558-22*shrink,w:w-108,h:bottom-(558-22*shrink)};}
  if(p.v===5){g.title={x:54,y:150,w:w-108,h:210};g.hero={x:54,y:380,w:w-108,h:470-80*shrink};g.people={x:54,y:g.hero.y+g.hero.h+30,w:w-108,h:bottom-(g.hero.y+g.hero.h+30)};}
  if(p.v===6){g.title={x:54,y:148,w:w-108,h:188};g.hero={x:54,y:348,w:w-108,h:245-40*shrink};g.people={x:54,y:g.hero.y+g.hero.h+26,w:w-108,h:bottom-(g.hero.y+g.hero.h+26)};}
  if(p.v===7){g.title={x:72,y:150,w:w-144,h:190};g.hero={x:0,y:128,w:w,h:320};g.people={x:54,y:446-16*shrink,w:w-108,h:bottom-(446-16*shrink)};}
  if(p.v===8){g.title={x:90,y:188,w:w-180,h:238};g.hero={x:0,y:128,w:w,h:500};g.people={x:54,y:654-18*shrink,w:w-108,h:bottom-(654-18*shrink)};}
  if(!p.s.images.hero){
   var titleH=p.v===5||p.v===8?250:p.v===1?120:[3,7].includes(p.v)?130:210,peopleY=150+titleH+(p.v===1?30:56);
   g.title={x:54,y:150,w:w-108,h:titleH};g.hero=null;
   g.people={x:54,y:peopleY,w:w-108,h:bottom-peopleY};
  }
  var r=recipe(p.v,count),items=[3,7,8].includes(p.v)?gridRects(1,count,.045).map(function(item){item.mode='left';return item;}):peopleRects(r.kind,count),needed=0;
  items.forEach(function(item,i){var person=p.s.speakers[i];if(!person)return;var cw=item.w*g.people.w,side=item.mode==='left',tw=side?cw*.70-32:cw-32;
   var texts=typed(p,'speaker',person.name,0,0,tw,22,700,api.C.ink,p.font).h+typed(p,'speaker',person.affiliation,0,0,tw,17,700,api.C.muted,p.font).h;
   var photo=side?Math.min(cw*.25,140):Math.min(cw,180);
   needed=Math.max(needed,(side?Math.max(photo,texts+48):photo+texts+48)/item.h);
  });
  if(g.hero){
   if([1,3,4,7].includes(p.v)){
    if(p.v===1){g.title={x:54,y:146,w:850,h:100};g.hero={x:940,y:146,w:w-994,h:100};}
    if([3,7].includes(p.v)){g.title={x:54,y:150,w:500,h:120};g.hero={x:590,y:150,w:w-644,h:120};}
    if(p.v===4){g.title.h=240;g.hero.h=240;}
    g.people.y=Math.max(g.title.y+g.title.h,g.hero.y+Math.min(g.hero.h,240))+56;g.hero.h=g.people.y-g.hero.y-56;}
   else {g.hero.y=g.title.y+g.title.h+42;g.hero.h=Math.max(90,Math.min(g.hero.h,bottom-g.hero.y-needed-56));g.people.y=g.hero.y+g.hero.h+56;}
   if(g.people.y+needed>bottom&&g.hero.h>90&&![1,3,4,7].includes(p.v)){var reduction=Math.min(g.hero.h-90,g.people.y+needed-bottom);g.hero.h-=reduction;g.people.y-=reduction;}
  }
  g.people.h=bottom-g.people.y;
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
  if(kind==='duoSide')return gridRects(2,1,.035).map(function(r){r.mode='panorama';return r;});
  if(kind==='panoramaTrio')return gridRects(3,1,.03).map(function(r){r.mode='panorama';return r;});
  if(kind==='rowFour')return gridRects(4,1,.025).map(function(r){r.mode='panorama';return r;});
  if(kind==='editorialDuo')return [rect(0,0,.485,1,'cover'),rect(.515,0,.485,1,'cover')];
  if(kind==='editorialColumns')return gridRects(3,1,.025).map(function(r){r.mode='cover';return r;});
  if(kind==='fullBleedFour')return gridRects(4,1,.012).map(function(r){r.mode='cover';return r;});
  if(kind==='squareDuo')return [rect(0,.10,.48,.80,'cover'),rect(.52,.10,.48,.80,'cover')];
  if(kind==='squareTrio')return [rect(0,.10,.31,.80,'cover'),rect(.345,.10,.31,.80,'cover'),rect(.69,.10,.31,.80,'cover')];
  if(kind==='squareGrid')return gridRects(2,2,.04);
  if(kind==='publicationDuo')return [rect(0,.04,.48,.92,'publication'),rect(.52,.04,.48,.92,'publication')];
  if(kind==='publicationTrio')return [rect(0,.04,.31,.92,'publication'),rect(.345,.04,.31,.92,'publication'),rect(.69,.04,.31,.92,'publication')];
  if(kind==='publicationGrid')return gridRects(2,2,.04);
  if(kind==='verticalTwo')return [rect(0,0,.485,1,'cover'),rect(.515,0,.485,1,'cover')];
  if(kind==='verticalThree')return gridRects(3,1,.025).map(function(r){r.mode='cover';return r;});
  if(kind==='verticalFour')return gridRects(4,1,.018).map(function(r){r.mode='cover';return r;});
  if(kind==='digitalDuo')return [rect(0,.08,.48,.84,'top'),rect(.52,.08,.48,.84,'top')];
  if(kind==='circleTrio')return [rect(0,.10,.30,.80,'circle'),rect(.35,.10,.30,.80,'circle'),rect(.70,.10,.30,.80,'circle')];
  if(kind==='digitalFour')return gridRects(4,1,.02);
  if(kind==='digitalSquareDuo')return [rect(0,.10,.48,.80,'cover'),rect(.52,.10,.48,.80,'cover')];
  if(kind==='digitalSquareTrio')return [rect(0,.10,.31,.80,'cover'),rect(.345,.10,.31,.80,'cover'),rect(.69,.10,.31,.80,'cover')];
  if(kind==='digitalSquareGrid')return gridRects(2,2,.04);
  if(kind==='storyRowsTwo')return [rect(0,0,1,.47,'left'),rect(0,.53,1,.47,'left')];
  if(kind==='storyRowsThree')return [rect(0,0,1,.30,'left'),rect(0,.35,1,.30,'left'),rect(0,.70,1,.30,'left')];
  if(kind==='storyGridFour')return gridRects(2,2,.04).map(function(r){r.mode='left';return r;});
  return gridRects(n>4?3:Math.max(1,n),Math.ceil(n/3),.025);
 }

 async function drawHero(ctx,p,g,audit){
  if(!g.hero||!p.s.images.hero)return;
  await api.coverImage(ctx,p.s.images.hero,g.hero.x,g.hero.y,g.hero.w,g.hero.h,null,12);
  audit.push({label:'hero-image',x:g.hero.x,y:g.hero.y,w:g.hero.w,h:g.hero.h,maxLine:0});
 }

 function drawTitle(ctx,p,g,audit){
  var a=g.title,pad=18,titleValue=p.v>=3&&(p.s.options.socialTitle||'').trim()?p.s.options.socialTitle:p.s.event.title;
  if(p.v===0)titleValue=titleValue.replace(/\s*\n\s*/g,' ');
  var subtitleValue=p.v>=3&&(p.s.options.socialSubtitle||'').trim()?p.s.options.socialSubtitle:p.s.event.subtitle;
  var theme=boxTheme(ctx,p,'title',a.x-pad,a.w+pad*2);
  api.box(ctx,a.x-pad,a.y-pad,a.w+pad*2,a.h+pad*2,theme.fill,16);
  audit.push({label:'title-box',x:a.x-pad,y:a.y-pad,w:a.w+pad*2,h:a.h+pad*2,maxLine:0});
  var max=p.v===0?76:p.v===5||p.v===8?72:p.v===1?60:68,align='center';
  var titleSpec=fittedType(p,'title',titleValue||'Título del evento',a.x,0,a.w,a.h,max,p.v>=3?28:34,700,theme.text,p.font,align,1.04);
  if(p.v===0)while(titleSpec.h>titleSpec.size*1.08&&titleSpec.size>66)titleSpec=text(titleSpec.text,titleSpec.x,0,titleSpec.w,titleSpec.size-1,titleSpec.weight,titleSpec.color,titleSpec.font,titleSpec.align,titleSpec.leading);
  var sub=fittedType(p,'title',subtitleValue,a.x,0,a.w,a.h,Math.max(22,Math.round(titleSpec.size*.46)),19,400,theme.muted,p.font,align,1.16);
  var items=[{spec:titleSpec,label:'event-title'},{spec:sub,label:'event-subtitle'}];
  for(var step=0;step<30&&items.reduce(function(sum,item){return sum+item.spec.h;},0)+(items.length-1)*12>a.h;step++){items.forEach(function(item){var t=item.spec,min=item.label==='event-title'?typeSize(p,null,28):typeSize(p,null,17);item.spec=text(t.text,t.x,0,t.w,Math.max(min,t.size-2),t.weight,t.color,t.font,t.align,t.leading);});}
  items.forEach(function(item){item.spec.overflow=false;});
  if(items.reduce(function(sum,item){return sum+item.spec.h;},0)+(items.length-1)*12>a.h)items[0].spec.overflow=true;
  drawStack(ctx,items,a.y,a.h,12,audit);
 }

 async function drawPerson(ctx,p,item,area,index,audit){
  var x=area.x+item.x*area.w,y=area.y+item.y*area.h,w=item.w*area.w,h=item.h*area.h,person=p.s.speakers[index];
  if(!person)return;
  var theme=boxTheme(ctx,p,'speaker',x,w);
  ctx.save();ctx.shadowColor='#14253624';ctx.shadowBlur=18;ctx.shadowOffsetY=8;api.box(ctx,x,y,w,h,theme.fill,12);ctx.restore();
  audit.push({label:'speaker-card-'+index,x:x,y:y,w:w,h:h,maxLine:0});
  var social=p.v>=3,nameSize=Math.max(p.v===5?24:20,Math.min(social?29:31,w*.082));
  function personStack(tx,tw,zoneH,align,target){
   var profile=target||person;
   var values=[{text:profile.name||'Nombre',label:'speaker-name-'+index,size:nameSize,min:18,weight:700,color:theme.text}];
   if(profile.affiliation)values.push({text:profile.affiliation,label:'speaker-affiliation-'+index,size:Math.max(18,nameSize*.72),min:16,weight:700,color:theme.muted});
   var items;
   for(var reduction=0;reduction<=20;reduction+=2){items=values.map(function(v){return {spec:typed(p,'speaker',v.text,tx,0,tw,Math.max(v.min,v.size-reduction),v.weight,v.color,p.font,align,1.14),label:v.label};});if(items.reduce(function(sum,item){return sum+item.spec.h;},0)+(items.length-1)*10<=zoneH+.5)break;}
   if(items.reduce(function(sum,item){return sum+item.spec.h;},0)+(items.length-1)*10>zoneH+.5)items[0].spec.overflow=true;
   return items;
  }
  if(item.mode==='left'){
   var photo=Math.min(h-16,w*.25);
   await api.drawAvatar(ctx,person,x+8,y+(h-photo)/2,photo,p.font,'rect');
   audit.push({label:'speaker-photo-'+index,x:x+8,y:y+(h-photo)/2,w:photo,h:photo,maxLine:0});
   var tx=x+photo+24,tw=w-photo-36;
   if([3,7,8].includes(p.v)){
    var nameW=tw*.33,detailX=tx+nameW+12,detailW=tw*.67-12;
    var name=fittedType(p,'speaker',person.name||'Nombre',tx,0,nameW,h-24,24,18,700,theme.text,p.font,'left',1.14);
    var detail=fitted(person.affiliation,detailX,0,detailW,h-24,typeSize(p,'speaker',18),17,400,theme.muted,p.font,'left',1.14);
    drawStack(ctx,[{spec:name,label:'speaker-name-'+index}],y+12,h-24,0,audit);
    drawStack(ctx,[{spec:detail,label:'speaker-affiliation-'+index}],y+12,h-24,0,audit);
   }else drawStack(ctx,personStack(tx,tw,h-20,'center'),y+10,h-20,10,audit);
   return;
  }
  if(item.mode==='circle'){
   var textH=Math.max.apply(null,p.s.speakers.map(function(profile){var items=personStack(x+16,w-32,0,'center',profile);return items.reduce(function(sum,item){return sum+item.spec.h;},0)+(items.length-1)*10+32;}));
   var circle=Math.max(40,Math.min(w*.82,h*.48,h-textH)),cx=x+(w-circle)/2;
   await api.drawAvatar(ctx,person,cx,y,circle,p.font,'circle');
   audit.push({label:'speaker-photo-'+index,x:cx,y:y,w:circle,h:circle,maxLine:0});
   drawStack(ctx,personStack(x+16,w-32,h-circle-32,'center'),y+circle+16,h-circle-32,10,audit);
   return;
  }
  var inset=14,minimumText=Math.max.apply(null,p.s.speakers.map(function(profile){var items=personStack(x+16,w-32,0,'center',profile);return items.reduce(function(sum,item){return sum+item.spec.h;},0)+(items.length-1)*10+32;}));
  var photoH=Math.max(32,Math.min(item.mode==='panorama'?Math.min(w-28,220):item.mode==='publication'?h*.60:item.mode==='cover'?h*(social?.62:.58):h*(social?.58:.50),h-minimumText-inset));
  if(person.photo)await api.portraitImage(ctx,person,x+inset,y+inset,w-inset*2,photoH,12,p.v===2||p.v===5?'lifted':'classic');
  else api.box(ctx,x+inset,y+inset,w-inset*2,photoH,'#e5e8ef',12);
  audit.push({label:'speaker-photo-'+index,x:x+inset,y:y+inset,w:w-inset*2,h:photoH,maxLine:0});
  var labelY=y+inset+photoH,backH=h-inset-photoH;
  audit.push({label:'speaker-text-zone-'+index,x:x+16,y:labelY,w:w-32,h:backH,maxLine:0});
  drawStack(ctx,personStack(x+16,w-32,backH-32,'center'),labelY+16,backH-32,10,audit);
 }

 async function drawPeople(ctx,p,g,r,audit){
  var area=g.people,items=peopleRects(r.kind,p.s.speakers.length);
  if([3,7,8].includes(p.v)){items=gridRects(1,p.s.speakers.length,.045).map(function(item){item.mode='left';return item;});p.composition=r.id+'-afiliaciones-amplias';}
  var theme=boxTheme(ctx,p,'speaker',area.x,area.w);
  var firstY=area.y+Math.min.apply(null,items.map(function(item){return item.y;}))*area.h;
  if(g.hero&&firstY-24<g.hero.y+g.hero.h&&firstY>g.hero.y){
   api.box(ctx,area.x-4,firstY-26,118,24,theme.fill,4);
  }
  drawTracked(ctx,typed(p,'speaker',p.s.speakers.length===1?'EXPONE':'EXPONEN',area.x,firstY-36,area.w,16,700,theme.muted,p.font), 'speaker-label',audit);
  for(var i=0;i<items.length&&i<p.s.speakers.length;i++)await drawPerson(ctx,p,items[i],area,i,audit);
 }

 async function drawModeration(ctx,p,g,audit){
  if(!p.s.moderators.length)return;
  var y=g.modsY,x=54,w=p.w-108,each=w/p.s.moderators.length;
  var theme=boxTheme(ctx,p,'moderator',x,w);
  api.box(ctx,x,y,w,g.modsH,theme.fill,10);
  audit.push({label:'moderator-box',x:x,y:y,w:w,h:g.modsH,maxLine:0});
  drawTracked(ctx,typed(p,'moderator',p.s.moderators.length===1?'MODERA':'MODERAN',x+12,y+10,w-24,16,700,theme.muted,p.font), 'moderation-label',audit);
  for(var i=0;i<p.s.moderators.length;i++){
   var person=p.s.moderators[i],px=x+i*each+12,photo=72,zoneY=y+36,zoneH=g.modsH-46;
   await api.drawAvatar(ctx,person,px,zoneY+(zoneH-photo)/2,photo,p.font,'circle');
   audit.push({label:'mod-photo-'+i,x:px,y:zoneY+(zoneH-photo)/2,w:photo,h:photo,maxLine:0});
   var tx=px+photo+12,tw=each-photo-54,items=[{spec:fittedType(p,'moderator',person.name||'Nombre',tx,0,tw,zoneH,18,16,700,theme.text,p.font,'left',1.06),label:'mod-name-'+i}];
   if(person.affiliation)items.push({spec:fittedType(p,'moderator',person.affiliation,tx,0,tw,zoneH,16,15,400,theme.muted,p.font,'left',1.08),label:'mod-affiliation-'+i});

   while(items.reduce(function(sum,item){return sum+item.spec.h;},0)+(items.length-1)*4>zoneH+.5&&items.some(function(item){return item.spec.size>17;}))items.forEach(function(item){var t=item.spec;item.spec=text(t.text,t.x,0,t.w,Math.max(17,t.size-1),t.weight,t.color,t.font,t.align,t.leading);});
   if(items.reduce(function(sum,item){return sum+item.spec.h;},0)+(items.length-1)*4>zoneH+.5)items[0].spec.overflow=true;
   drawStack(ctx,items,zoneY,zoneH,4,audit);
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
  var x=54,y=g.meetingY,w=p.w-108,h=g.meetingH,left=w*.44,rightX=x+w*.49,social=p.v>=3;
  var qr=api.getQR({options:{showQR:social?p.s.options.socialQR:p.s.options.showQR},event:p.s.event});
  var qrSize=qr?Math.min(96,h-28):0,rightW=w*.47-(qrSize?qrSize+16:0);
  var theme=boxTheme(ctx,p,'meeting',x,w);
  api.box(ctx,x,y,w,h,theme.fill,12);
  audit.push({label:'meeting-box',x:x,y:y,w:w,h:h,maxLine:0});
  var timeValue=p.s.event.time?(p.s.event.time+(p.s.event.endTime?' – '+p.s.event.endTime:'')+' h'):'Horario por confirmar';
  drawStack(ctx,[
   {spec:fittedType(p,'meeting',dateLabel(p.s),x+18,0,left-28,h*.34,27,19,700,theme.text,p.font,'center'),label:'meeting-date'},
   {spec:typed(p,'meeting',timeValue,x+18,0,left-28,21,400,theme.text,p.font,'center'),label:'meeting-time'},
   {spec:typed(p,'meeting',p.s.event.timezone,x+18,0,left-28,17,400,theme.muted,p.font,'center'),label:'meeting-zone'}
  ],y+14,h-28,7,audit);
  var platform=fittedType(p,'meeting',p.s.event.platform,rightX,0,rightW,h*.24,21,17,700,theme.text,p.font,'center');
  var location=p.s.event.location?fittedType(p,'meeting',p.s.event.location,rightX,0,rightW,h*.24,17,15,400,theme.muted,p.font,'center'):null;
  var url=visibleURL(p.s);
  while(text(url,0,0,rightW-58,typeSize(p,null,17),700,'#fff',p.font).lines.length>1&&url.length>12)url=url.slice(0,-2)+'…';
  var linkH=44,total=platform.h+8+linkH+(location?8+location.h:0),rightY=y+(h-total)/2;
  platform.y=rightY;drawTracked(ctx,platform,'meeting-platform',audit);rightY+=platform.h+8;
  var linkX=rightX,linkY=rightY-3,fill=ctx.createLinearGradient(linkX,linkY,linkX+rightW,linkY+linkH);
  fill.addColorStop(0,'#142536');fill.addColorStop(1,'#0062ad');
  ctx.save();ctx.shadowColor='#0062ad30';ctx.shadowBlur=12;ctx.shadowOffsetY=4;api.box(ctx,linkX,linkY,rightW,linkH,fill,linkH/2);ctx.restore();
  api.box(ctx,linkX+10,linkY+10,30,24,'#ffffff24',8);ctx.fillStyle='#ffffff';ctx.beginPath();ctx.moveTo(linkX+21,linkY+16);ctx.lineTo(linkX+31,linkY+22);ctx.lineTo(linkX+21,linkY+28);ctx.fill();
  audit.push({label:'meeting-link-box',x:linkX,y:linkY,w:rightW,h:linkH,maxLine:0});
  drawStack(ctx,[{spec:fittedType(p,'meeting',url,linkX+46,0,rightW-58,linkH-10,17,13,700,'#fff',p.font,'center'),label:'meeting-link'}],linkY,linkH,0,audit);
  if(location){location.y=rightY+linkH+5;drawTracked(ctx,location,'meeting-location',audit);}
  if(qr){var qrX=x+w-qrSize-12,qrY=y+(h-qrSize)/2;api.drawQR(ctx,qr,qrX,qrY,qrSize);audit.push({label:'meeting-qr',x:qrX,y:qrY,w:qrSize,h:qrSize,maxLine:0});}
 }

 async function drawFooter(ctx,p,g,audit){
  var y=g.footerTop,height=p.h-y;
  ctx.save();ctx.shadowColor='#14253645';ctx.shadowBlur=18;ctx.shadowOffsetY=-8;api.box(ctx,0,y,p.w,p.h-y,'rgba(255,255,255,.96)');ctx.restore();
  api.line(ctx,44,y,p.w-44,y,'#d4d9e5');
  await api.containImage(ctx,api.BRAND_ASSETS['isotipo-color'],54,y+18,66,height-36);
  audit.push({label:'footer-logo',x:54,y:y+18,w:66,h:height-36,maxLine:0});
  drawStack(ctx,[{spec:typed(p,null,'redplacts.org',140,0,300,22,700,api.C.ink,p.font,'left'),label:'footer-website'}],y+14,height-28,0,audit);
  var networks=[['Instagram','@redplacts'],['X','@PlactsRed'],['Facebook','@redplacts'],['YouTube','@RedPLACTS']],step=132,start=p.w-54-step*networks.length;
  for(var i=0;i<networks.length;i++)drawStack(ctx,[
   {spec:typed(p,null,networks[i][0],start+i*step,0,step-10,15,700,api.C.ink,p.font,'center'),label:'footer-network-'+i},
   {spec:typed(p,null,networks[i][1],start+i*step,0,step-10,14,400,api.C.muted,p.font,'center'),label:'footer-handle-'+i}
  ],y+14,height-28,3,audit);
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
