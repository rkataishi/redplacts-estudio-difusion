/* designs.js — renderer visual versionado para los nueve outputs. */
(function(){
 'use strict';

 async function draw(p, scale, api){
  const {canvas, ctx, audit} = api.newCanvas(p, scale);
  api.box(ctx, 0, 0, p.w, p.h, '#fafafa');
  return {canvas, audit};
 }

 window.RedPlactsDesigns = {draw};

 if(typeof module!=='undefined'&&module.exports) module.exports={draw};
})();
