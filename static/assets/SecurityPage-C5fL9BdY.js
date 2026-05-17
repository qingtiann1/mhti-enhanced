import{d as D,R as a,ao as P,an as H,ap as T,aY as F,ar as M,as as A,aM as U,v as Q,aw as W,bP as Y,b as q,u as G,bQ as J,r as S,f as K,c as I,j as h,k as o,w as n,x as V,o as k,N as L,I as R,F as X,y as Z,ag as ee,ah as te,a as N,A as B,s as $,D as E,L as ae,B as O,l as j,aj as se,a5 as re,bR as ne,bS as oe,bT as le,bU as ie,bV as ce,_ as de}from"./index-CxuZ4q-t.js";const ue=D({name:"ArrowBack",render(){return a("svg",{xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 24 24"},a("path",{d:"M0 0h24v24H0V0z",fill:"none"}),a("path",{d:"M19 11H7.83l4.88-4.88c.39-.39.39-1.03 0-1.42-.39-.39-1.02-.39-1.41 0l-6.59 6.59c-.39.39-.39 1.02 0 1.41l6.59 6.59c.39.39 1.02.39 1.41 0 .39-.39.39-1.02 0-1.41L7.83 13H19c.55 0 1-.45 1-1s-.45-1-1-1z"}))}}),ge=P([H("page-header-header",`
 margin-bottom: 20px;
 `),H("page-header",`
 display: flex;
 align-items: center;
 justify-content: space-between;
 line-height: 1.5;
 font-size: var(--n-font-size);
 `,[T("main",`
 display: flex;
 flex-wrap: nowrap;
 align-items: center;
 `),T("back",`
 display: flex;
 margin-right: 16px;
 font-size: var(--n-back-size);
 cursor: pointer;
 color: var(--n-back-color);
 transition: color .3s var(--n-bezier);
 `,[P("&:hover","color: var(--n-back-color-hover);"),P("&:active","color: var(--n-back-color-pressed);")]),T("avatar",`
 display: flex;
 margin-right: 12px
 `),T("title",`
 margin-right: 16px;
 transition: color .3s var(--n-bezier);
 font-size: var(--n-title-font-size);
 font-weight: var(--n-title-font-weight);
 color: var(--n-title-text-color);
 `),T("subtitle",`
 font-size: 14px;
 transition: color .3s var(--n-bezier);
 color: var(--n-subtitle-text-color);
 `)]),H("page-header-content",`
 font-size: var(--n-font-size);
 `,[P("&:not(:first-child)","margin-top: 20px;")]),H("page-header-footer",`
 font-size: var(--n-font-size);
 `,[P("&:not(:first-child)","margin-top: 20px;")])]),pe=Object.assign(Object.assign({},A.props),{title:String,subtitle:String,extra:String,onBack:Function}),he=D({name:"PageHeader",props:pe,slots:Object,setup(f){const{mergedClsPrefixRef:i,mergedRtlRef:c,inlineThemeDisabled:v}=M(f),u=A("PageHeader","-page-header",ge,Y,f,i),t=U("PageHeader",c,i),m=Q(()=>{const{self:{titleTextColor:y,subtitleTextColor:d,backColor:_,fontSize:g,titleFontSize:x,backSize:p,titleFontWeight:b,backColorHover:w,backColorPressed:z},common:{cubicBezierEaseInOut:C}}=u.value;return{"--n-title-text-color":y,"--n-title-font-size":x,"--n-title-font-weight":b,"--n-font-size":g,"--n-back-size":p,"--n-subtitle-text-color":d,"--n-back-color":_,"--n-back-color-hover":w,"--n-back-color-pressed":z,"--n-bezier":C}}),l=v?W("page-header",void 0,m,f):void 0;return{rtlEnabled:t,mergedClsPrefix:i,cssVars:v?void 0:m,themeClass:l?.themeClass,onRender:l?.onRender}},render(){var f;const{onBack:i,title:c,subtitle:v,extra:u,mergedClsPrefix:t,cssVars:m,$slots:l}=this;(f=this.onRender)===null||f===void 0||f.call(this);const{title:y,subtitle:d,extra:_,default:g,header:x,avatar:p,footer:b,back:w}=l,z=i,C=c||y,e=v||d,s=u||_;return a("div",{style:m,class:[`${t}-page-header-wrapper`,this.themeClass,this.rtlEnabled&&`${t}-page-header-wrapper--rtl`]},x?a("div",{class:`${t}-page-header-header`,key:"breadcrumb"},x()):null,(z||p||C||e||s)&&a("div",{class:`${t}-page-header`,key:"header"},a("div",{class:`${t}-page-header__main`,key:"back"},z?a("div",{class:`${t}-page-header__back`,onClick:i},w?w():a(F,{clsPrefix:t},{default:()=>a(ue,null)})):null,p?a("div",{class:`${t}-page-header__avatar`},p()):null,C?a("div",{class:`${t}-page-header__title`,key:"title"},c||y()):null,e?a("div",{class:`${t}-page-header__subtitle`,key:"subtitle"},v||d()):null),s?a("div",{class:`${t}-page-header__extra`},u||_()):null),g?a("div",{class:`${t}-page-header-content`,key:"content"},g()):null,b?a("div",{class:`${t}-page-header-footer`,key:"footer"},b()):null)}}),fe={class:"security-page"},ve={key:0,class:"empty-state"},me={class:"session-info"},be=D({__name:"SecurityPage",setup(f){const i=q(),c=G(),v=J(),u=S([]),t=S(!1),m=S([]),l=S(!1),y=S(0),d=S({page:1,pageSize:10,itemCount:0,showSizePicker:!1});function _(e){switch(e){case"mobile":return le;case"tablet":return oe;default:return ne}}function g(e){return new Date(e).toLocaleString("zh-CN",{year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit"})}const x=[{title:"状态",key:"success",width:80,render(e){return a(j,{size:20,color:e.success?"#18a058":"#d03050",component:e.success?ie:ce})}},{title:"设备",key:"device_name",ellipsis:{tooltip:!0},render(e){return e.device_name||"未知设备"}},{title:"IP 地址",key:"ip_address",width:140},{title:"登录时间",key:"login_time",width:170,render(e){return g(e.login_time)}},{title:"失败原因",key:"failure_reason",ellipsis:{tooltip:!0},render(e){return e.failure_reason||"-"}}];async function p(){t.value=!0;try{u.value=await i.getSessions()}catch{c.error("加载会话列表失败")}finally{t.value=!1}}async function b(e=1){l.value=!0;try{const s=(e-1)*d.value.pageSize,r=await i.getLoginHistory(d.value.pageSize,s);m.value=r.items,y.value=r.total,d.value.itemCount=r.total,d.value.page=e}catch{c.error("加载登录历史失败")}finally{l.value=!1}}async function w(e){v.warning({title:"确认注销",content:"确定要注销该设备的登录状态吗？",positiveText:"确定",negativeText:"取消",onPositiveClick:async()=>{try{await i.revokeSession(e),c.success("会话已注销"),await p()}catch{c.error("注销失败")}}})}async function z(){v.warning({title:"确认注销",content:"确定要注销所有其他设备的登录状态吗？",positiveText:"确定",negativeText:"取消",onPositiveClick:async()=>{try{await i.revokeAllSessions(),c.success("已注销所有其他会话"),await p()}catch{c.error("注销失败")}}})}function C(e){b(e)}return K(()=>{p(),b()}),(e,s)=>(k(),I("div",fe,[h(o(he),{title:"安全设置",subtitle:"管理登录会话和查看登录历史"}),h(o(V),{title:"活跃会话",class:"section-card"},{"header-extra":n(()=>[h(o(O),{size:"small",type:"error",ghost:"",disabled:u.value.length<=1,onClick:z},{default:n(()=>[...s[0]||(s[0]=[$(" 注销其他设备 ",-1)])]),_:1},8,["disabled"])]),default:n(()=>[h(o(L),{show:t.value},{default:n(()=>[u.value.length===0?(k(),I("div",ve," 暂无活跃会话 ")):(k(),R(o(se),{key:1},{default:n(()=>[(k(!0),I(X,null,Z(u.value,r=>(k(),R(o(ee),{key:r.id},{prefix:n(()=>[h(o(j),{size:"24",component:_(r.device_type)},null,8,["component"])]),suffix:n(()=>[r.is_current?E("",!0):(k(),R(o(O),{key:0,size:"small",type:"error",ghost:"",onClick:ke=>w(r.id)},{default:n(()=>[...s[2]||(s[2]=[$(" 注销 ",-1)])]),_:1},8,["onClick"]))]),default:n(()=>[h(o(te),null,{header:n(()=>[$(B(r.device_name)+" ",1),r.is_current?(k(),R(o(ae),{key:0,type:"success",size:"small",class:"current-tag"},{default:n(()=>[...s[1]||(s[1]=[$(" 当前设备 ",-1)])]),_:1})):E("",!0)]),description:n(()=>[N("div",me,[N("span",null,"IP: "+B(r.ip_address),1),N("span",null,"登录时间: "+B(g(r.created_at)),1),N("span",null,"最后活跃: "+B(g(r.last_used_at)),1),N("span",null,"过期时间: "+B(g(r.expires_at)),1)])]),_:2},1024)]),_:2},1024))),128))]),_:1}))]),_:1},8,["show"])]),_:1}),h(o(V),{title:"登录历史",class:"section-card"},{default:n(()=>[h(o(L),{show:l.value},{default:n(()=>[h(o(re),{columns:x,data:m.value,pagination:d.value,remote:!0,"onUpdate:page":C},null,8,["data","pagination"])]),_:1},8,["show"])]),_:1})]))}}),_e=de(be,[["__scopeId","data-v-edb65709"]]);export{_e as default};
