import{b3 as ue,bI as he,bs as be,an as P,ap as t,ao as A,aq as d,aI as I,bw as E,d as q,bJ as K,R as i,T as w,by as fe,bK as ve,ar as ge,as as X,b6 as we,r as M,av as pe,aK as me,v as z,be as p,bE as D,bL as c,aw as xe,aN as U,c as ye,o as ke,a as H,af as L}from"./index-CxuZ4q-t.js";function Ce(e){const{primaryColor:r,opacityDisabled:n,borderRadius:l,textColor3:s}=e;return Object.assign(Object.assign({},he),{iconColor:s,textColor:"white",loadingColor:r,opacityDisabled:n,railColor:"rgba(0, 0, 0, .14)",railColorActive:r,buttonBoxShadow:"0 1px 4px 0 rgba(0, 0, 0, 0.3), inset 0 0 1px 0 rgba(0, 0, 0, 0.05)",buttonColor:"#FFF",railBorderRadiusSmall:l,railBorderRadiusMedium:l,railBorderRadiusLarge:l,buttonBorderRadiusSmall:l,buttonBorderRadiusMedium:l,buttonBorderRadiusLarge:l,boxShadowFocus:`0 0 0 2px ${be(r,{alpha:.2})}`})}const Be={common:ue,self:Ce},Se=P("switch",`
 height: var(--n-height);
 min-width: var(--n-width);
 vertical-align: middle;
 user-select: none;
 -webkit-user-select: none;
 display: inline-flex;
 outline: none;
 justify-content: center;
 align-items: center;
`,[t("children-placeholder",`
 height: var(--n-rail-height);
 display: flex;
 flex-direction: column;
 overflow: hidden;
 pointer-events: none;
 visibility: hidden;
 `),t("rail-placeholder",`
 display: flex;
 flex-wrap: none;
 `),t("button-placeholder",`
 width: calc(1.75 * var(--n-rail-height));
 height: var(--n-rail-height);
 `),P("base-loading",`
 position: absolute;
 top: 50%;
 left: 50%;
 transform: translateX(-50%) translateY(-50%);
 font-size: calc(var(--n-button-width) - 4px);
 color: var(--n-loading-color);
 transition: color .3s var(--n-bezier);
 `,[E({left:"50%",top:"50%",originalTransform:"translateX(-50%) translateY(-50%)"})]),t("checked, unchecked",`
 transition: color .3s var(--n-bezier);
 color: var(--n-text-color);
 box-sizing: border-box;
 position: absolute;
 white-space: nowrap;
 top: 0;
 bottom: 0;
 display: flex;
 align-items: center;
 line-height: 1;
 `),t("checked",`
 right: 0;
 padding-right: calc(1.25 * var(--n-rail-height) - var(--n-offset));
 `),t("unchecked",`
 left: 0;
 justify-content: flex-end;
 padding-left: calc(1.25 * var(--n-rail-height) - var(--n-offset));
 `),A("&:focus",[t("rail",`
 box-shadow: var(--n-box-shadow-focus);
 `)]),d("round",[t("rail","border-radius: calc(var(--n-rail-height) / 2);",[t("button","border-radius: calc(var(--n-button-height) / 2);")])]),I("disabled",[I("icon",[d("rubber-band",[d("pressed",[t("rail",[t("button","max-width: var(--n-button-width-pressed);")])]),t("rail",[A("&:active",[t("button","max-width: var(--n-button-width-pressed);")])]),d("active",[d("pressed",[t("rail",[t("button","left: calc(100% - var(--n-offset) - var(--n-button-width-pressed));")])]),t("rail",[A("&:active",[t("button","left: calc(100% - var(--n-offset) - var(--n-button-width-pressed));")])])])])])]),d("active",[t("rail",[t("button","left: calc(100% - var(--n-button-width) - var(--n-offset))")])]),t("rail",`
 overflow: hidden;
 height: var(--n-rail-height);
 min-width: var(--n-rail-width);
 border-radius: var(--n-rail-border-radius);
 cursor: pointer;
 position: relative;
 transition:
 opacity .3s var(--n-bezier),
 background .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier);
 background-color: var(--n-rail-color);
 `,[t("button-icon",`
 color: var(--n-icon-color);
 transition: color .3s var(--n-bezier);
 font-size: calc(var(--n-button-height) - 4px);
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 display: flex;
 justify-content: center;
 align-items: center;
 line-height: 1;
 `,[E()]),t("button",`
 align-items: center; 
 top: var(--n-offset);
 left: var(--n-offset);
 height: var(--n-button-height);
 width: var(--n-button-width-pressed);
 max-width: var(--n-button-width);
 border-radius: var(--n-button-border-radius);
 background-color: var(--n-button-color);
 box-shadow: var(--n-button-box-shadow);
 box-sizing: border-box;
 cursor: inherit;
 content: "";
 position: absolute;
 transition:
 background-color .3s var(--n-bezier),
 left .3s var(--n-bezier),
 opacity .3s var(--n-bezier),
 max-width .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier);
 `)]),d("active",[t("rail","background-color: var(--n-rail-color-active);")]),d("loading",[t("rail",`
 cursor: wait;
 `)]),d("disabled",[t("rail",`
 cursor: not-allowed;
 opacity: .5;
 `)])]),Re=Object.assign(Object.assign({},X.props),{size:{type:String,default:"medium"},value:{type:[String,Number,Boolean],default:void 0},loading:Boolean,defaultValue:{type:[String,Number,Boolean],default:!1},disabled:{type:Boolean,default:void 0},round:{type:Boolean,default:!0},"onUpdate:value":[Function,Array],onUpdateValue:[Function,Array],checkedValue:{type:[String,Number,Boolean],default:!0},uncheckedValue:{type:[String,Number,Boolean],default:!1},railStyle:Function,rubberBand:{type:Boolean,default:!0},onChange:[Function,Array]});let S;const Ve=q({name:"Switch",props:Re,slots:Object,setup(e){S===void 0&&(typeof CSS<"u"?typeof CSS.supports<"u"?S=CSS.supports("width","max(1px)"):S=!1:S=!0);const{mergedClsPrefixRef:r,inlineThemeDisabled:n}=ge(e),l=X("Switch","-switch",Se,Be,e,r),s=we(e),{mergedSizeRef:y,mergedDisabledRef:v}=s,k=M(e.defaultValue),R=pe(e,"value"),g=me(R,k),C=z(()=>g.value===e.checkedValue),m=M(!1),a=M(!1),u=z(()=>{const{railStyle:o}=e;if(o)return o({focused:a.value,checked:C.value})});function h(o){const{"onUpdate:value":$,onChange:_,onUpdateValue:V}=e,{nTriggerFormInput:F,nTriggerFormChange:N}=s;$&&U($,o),V&&U(V,o),_&&U(_,o),k.value=o,F(),N()}function Y(){const{nTriggerFormFocus:o}=s;o()}function J(){const{nTriggerFormBlur:o}=s;o()}function G(){e.loading||v.value||(g.value!==e.checkedValue?h(e.checkedValue):h(e.uncheckedValue))}function Q(){a.value=!0,Y()}function Z(){a.value=!1,J(),m.value=!1}function ee(o){e.loading||v.value||o.key===" "&&(g.value!==e.checkedValue?h(e.checkedValue):h(e.uncheckedValue),m.value=!1)}function te(o){e.loading||v.value||o.key===" "&&(o.preventDefault(),m.value=!0)}const W=z(()=>{const{value:o}=y,{self:{opacityDisabled:$,railColor:_,railColorActive:V,buttonBoxShadow:F,buttonColor:N,boxShadowFocus:oe,loadingColor:ae,textColor:ne,iconColor:ie,[p("buttonHeight",o)]:b,[p("buttonWidth",o)]:re,[p("buttonWidthPressed",o)]:le,[p("railHeight",o)]:f,[p("railWidth",o)]:B,[p("railBorderRadius",o)]:se,[p("buttonBorderRadius",o)]:de},common:{cubicBezierEaseInOut:ce}}=l.value;let T,j,O;return S?(T=`calc((${f} - ${b}) / 2)`,j=`max(${f}, ${b})`,O=`max(${B}, calc(${B} + ${b} - ${f}))`):(T=D((c(f)-c(b))/2),j=D(Math.max(c(f),c(b))),O=c(f)>c(b)?B:D(c(B)+c(b)-c(f))),{"--n-bezier":ce,"--n-button-border-radius":de,"--n-button-box-shadow":F,"--n-button-color":N,"--n-button-width":re,"--n-button-width-pressed":le,"--n-button-height":b,"--n-height":j,"--n-offset":T,"--n-opacity-disabled":$,"--n-rail-border-radius":se,"--n-rail-color":_,"--n-rail-color-active":V,"--n-rail-height":f,"--n-rail-width":B,"--n-width":O,"--n-box-shadow-focus":oe,"--n-loading-color":ae,"--n-text-color":ne,"--n-icon-color":ie}}),x=n?xe("switch",z(()=>y.value[0]),W,e):void 0;return{handleClick:G,handleBlur:Z,handleFocus:Q,handleKeyup:ee,handleKeydown:te,mergedRailStyle:u,pressed:m,mergedClsPrefix:r,mergedValue:g,checked:C,mergedDisabled:v,cssVars:n?void 0:W,themeClass:x?.themeClass,onRender:x?.onRender}},render(){const{mergedClsPrefix:e,mergedDisabled:r,checked:n,mergedRailStyle:l,onRender:s,$slots:y}=this;s?.();const{checked:v,unchecked:k,icon:R,"checked-icon":g,"unchecked-icon":C}=y,m=!(K(R)&&K(g)&&K(C));return i("div",{role:"switch","aria-checked":n,class:[`${e}-switch`,this.themeClass,m&&`${e}-switch--icon`,n&&`${e}-switch--active`,r&&`${e}-switch--disabled`,this.round&&`${e}-switch--round`,this.loading&&`${e}-switch--loading`,this.pressed&&`${e}-switch--pressed`,this.rubberBand&&`${e}-switch--rubber-band`],tabindex:this.mergedDisabled?void 0:0,style:this.cssVars,onClick:this.handleClick,onFocus:this.handleFocus,onBlur:this.handleBlur,onKeyup:this.handleKeyup,onKeydown:this.handleKeydown},i("div",{class:`${e}-switch__rail`,"aria-hidden":"true",style:l},w(v,a=>w(k,u=>a||u?i("div",{"aria-hidden":!0,class:`${e}-switch__children-placeholder`},i("div",{class:`${e}-switch__rail-placeholder`},i("div",{class:`${e}-switch__button-placeholder`}),a),i("div",{class:`${e}-switch__rail-placeholder`},i("div",{class:`${e}-switch__button-placeholder`}),u)):null)),i("div",{class:`${e}-switch__button`},w(R,a=>w(g,u=>w(C,h=>i(fe,null,{default:()=>this.loading?i(ve,{key:"loading",clsPrefix:e,strokeWidth:20}):this.checked&&(u||a)?i("div",{class:`${e}-switch__button-icon`,key:u?"checked-icon":"icon"},u||a):!this.checked&&(h||a)?i("div",{class:`${e}-switch__button-icon`,key:h?"unchecked-icon":"icon"},h||a):null})))),w(v,a=>a&&i("div",{key:"checked",class:`${e}-switch__checked`},a)),w(k,a=>a&&i("div",{key:"unchecked",class:`${e}-switch__unchecked`},a)))))}}),$e={xmlns:"http://www.w3.org/2000/svg","xmlns:xlink":"http://www.w3.org/1999/xlink",viewBox:"0 0 512 512"},ze=q({name:"ArrowUpOutline",render:function(r,n){return ke(),ye("svg",$e,n[0]||(n[0]=[H("path",{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"48",d:"M112 244l144-144l144 144"},null,-1),H("path",{fill:"none",stroke:"currentColor","stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"48",d:"M256 120v292"},null,-1)]))}}),Fe={async browse(e="",r=1,n=20){return(await L.get("/files/browse",{params:{path:e,page:r,page_size:n}})).data},async scan(e,r=!0){const n={folder_path:e,exclude_scraped:r};return(await L.post("/scan",n)).data}};export{ze as A,Ve as N,Fe as f};
