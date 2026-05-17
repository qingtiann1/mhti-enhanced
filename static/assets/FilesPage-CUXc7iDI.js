import{an as F,ao as z,ap as E,aq as ve,d as H,R as C,ar as pe,as as ae,at as he,au as fe,av as ge,v as S,aw as be,ax as ke,r as h,f as _e,a2 as Ce,ay as ye,az as xe,aA as we,u as Be,G as ze,a9 as Pe,z as Re,c as x,j as u,w as p,k as r,x as Se,g as Te,o as n,a as d,I as P,D as N,l as w,aB as Le,s as V,B as q,F as A,y as X,A as I,p as Fe,J as Ne,n as $e,K as Y,ab as Ee,a5 as Ie,a6 as Me,_ as Oe}from"./index-CxuZ4q-t.js";import{f as qe}from"./files-BfGyb9Th.js";import{E as W}from"./EmptyState-DVDG0EDu.js";import{P as Ae,C as De,T as je}from"./PageSkeleton-w5hCK_p1.js";import{M as Ke}from"./ManualJobCreateModal-H6bp8wI-.js";import{S as Ve,D as ee}from"./watcher-dR84ea_g.js";import{A as Ue}from"./ArrowBackOutline-BYizex_m.js";import{A as U}from"./AddOutline-CbyVV-xS.js";import"./TouchCard.vue_vue_type_style_index_0_scoped_e25cced8_lang-Dm7gIYGR.js";import"./Grid-CgDq7D3p.js";import"./config-BoaPOlPN.js";import"./FolderBrowserModal-CkAtMqe1.js";import"./CheckmarkOutline-MtEELyW4.js";import"./Form-UbdV-RKH.js";const He=F("breadcrumb",`
 white-space: nowrap;
 cursor: default;
 line-height: var(--n-item-line-height);
`,[z("ul",`
 list-style: none;
 padding: 0;
 margin: 0;
 `),z("a",`
 color: inherit;
 text-decoration: inherit;
 `),F("breadcrumb-item",`
 font-size: var(--n-font-size);
 transition: color .3s var(--n-bezier);
 display: inline-flex;
 align-items: center;
 `,[F("icon",`
 font-size: 18px;
 vertical-align: -.2em;
 transition: color .3s var(--n-bezier);
 color: var(--n-item-text-color);
 `),z("&:not(:last-child)",[ve("clickable",[E("link",`
 cursor: pointer;
 `,[z("&:hover",`
 background-color: var(--n-item-color-hover);
 `),z("&:active",`
 background-color: var(--n-item-color-pressed); 
 `)])])]),E("link",`
 padding: 4px;
 border-radius: var(--n-item-border-radius);
 transition:
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 color: var(--n-item-text-color);
 position: relative;
 `,[z("&:hover",`
 color: var(--n-item-text-color-hover);
 `,[F("icon",`
 color: var(--n-item-text-color-hover);
 `)]),z("&:active",`
 color: var(--n-item-text-color-pressed);
 `,[F("icon",`
 color: var(--n-item-text-color-pressed);
 `)])]),E("separator",`
 margin: 0 8px;
 color: var(--n-separator-color);
 transition: color .3s var(--n-bezier);
 user-select: none;
 -webkit-user-select: none;
 `),z("&:last-child",[E("link",`
 font-weight: var(--n-font-weight-active);
 cursor: unset;
 color: var(--n-item-text-color-active);
 `,[F("icon",`
 color: var(--n-item-text-color-active);
 `)]),E("separator",`
 display: none;
 `)])])]),oe=ke("n-breadcrumb"),Ge=Object.assign(Object.assign({},ae.props),{separator:{type:String,default:"/"}}),Je=H({name:"Breadcrumb",props:Ge,setup(o){const{mergedClsPrefixRef:l,inlineThemeDisabled:k}=pe(o),f=ae("Breadcrumb","-breadcrumb",He,he,o,l);fe(oe,{separatorRef:ge(o,"separator"),mergedClsPrefixRef:l});const B=S(()=>{const{common:{cubicBezierEaseInOut:_},self:{separatorColor:c,itemTextColor:m,itemTextColorHover:g,itemTextColorPressed:v,itemTextColorActive:R,fontSize:b,fontWeightActive:y,itemBorderRadius:T,itemColorHover:$,itemColorPressed:D,itemLineHeight:j}}=f.value;return{"--n-font-size":b,"--n-bezier":_,"--n-item-text-color":m,"--n-item-text-color-hover":g,"--n-item-text-color-pressed":v,"--n-item-text-color-active":R,"--n-separator-color":c,"--n-item-color-hover":$,"--n-item-color-pressed":D,"--n-item-border-radius":T,"--n-font-weight-active":y,"--n-item-line-height":j}}),i=k?be("breadcrumb",void 0,B,o):void 0;return{mergedClsPrefix:l,cssVars:k?void 0:B,themeClass:i?.themeClass,onRender:i?.onRender}},render(){var o;return(o=this.onRender)===null||o===void 0||o.call(this),C("nav",{class:[`${this.mergedClsPrefix}-breadcrumb`,this.themeClass],style:this.cssVars,"aria-label":"Breadcrumb"},C("ul",null,this.$slots))}});function Ze(o=ye?window:null){const l=()=>{const{hash:B,host:i,hostname:_,href:c,origin:m,pathname:g,port:v,protocol:R,search:b}=o?.location||{};return{hash:B,host:i,hostname:_,href:c,origin:m,pathname:g,port:v,protocol:R,search:b}},k=h(l()),f=()=>{k.value=l()};return _e(()=>{o&&(o.addEventListener("popstate",f),o.addEventListener("hashchange",f))}),Ce(()=>{o&&(o.removeEventListener("popstate",f),o.removeEventListener("hashchange",f))}),k}const Qe={separator:String,href:String,clickable:{type:Boolean,default:!0},onClick:Function},te=H({name:"BreadcrumbItem",props:Qe,slots:Object,setup(o,{slots:l}){const k=xe(oe,null);if(!k)return()=>null;const{separatorRef:f,mergedClsPrefixRef:B}=k,i=Ze(),_=S(()=>o.href?"a":"span"),c=S(()=>i.value.href===o.href?"location":null);return()=>{const{value:m}=B;return C("li",{class:[`${m}-breadcrumb-item`,o.clickable&&`${m}-breadcrumb-item--clickable`]},C(_.value,{class:`${m}-breadcrumb-item__link`,"aria-current":c.value,href:o.href,onClick:o.onClick},l),C("span",{class:`${m}-breadcrumb-item__separator`,"aria-hidden":"true"},we(l.separator,()=>{var g;return[(g=o.separator)!==null&&g!==void 0?g:f.value]})))}}}),Xe={class:"files-page"},Ye={class:"page-header"},We={class:"header-left"},et={class:"breadcrumb-bar"},tt={class:"toolbar"},at={class:"toolbar-left"},ot={class:"toolbar-right"},rt={class:"selected-count"},st={key:0,class:"mobile-file-list"},nt={class:"file-card-content"},it={class:"file-info"},lt={class:"file-name-text"},ct={class:"file-meta"},ut={key:0,class:"file-size"},dt={key:1,class:"file-time"},mt={class:"file-actions"},vt={key:3,class:"pagination"},pt=H({__name:"FilesPage",setup(o){const l=Pe(),k=Te(),f=Be(),{isMobile:B}=ze(),i=h(!1),_=h([]),c=h(""),m=h(null),g=h(0),v=h(1),R=h(20),b=h(""),y=h([]),T=h(!1),$=h(""),D=S(()=>l.query.root||""),j=S(()=>parseInt(l.query.page)||1),re=S(()=>{if(!c.value)return[];const e=[],a=c.value.split(/[/\\]/).filter(Boolean);if(c.value.match(/^[A-Z]:\\/i)){let s="";a.forEach((t,O)=>{O===0?(s=t+"\\",e.push({name:t,path:s})):(s=s+t+"\\",e.push({name:t,path:s.slice(0,-1)}))})}else{let s="";a.forEach(t=>{s=s+"/"+t,e.push({name:t,path:s})})}return e}),G=e=>e===null?"-":e<1024?`${e} B`:e<1024*1024?`${(e/1024).toFixed(1)} KB`:e<1024*1024*1024?`${(e/1024/1024).toFixed(1)} MB`:`${(e/1024/1024/1024).toFixed(2)} GB`,J=e=>e?new Date(e).toLocaleString("zh-CN",{year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit"}):"-",M=S(()=>{if(!b.value)return _.value;const e=b.value.toLowerCase();return _.value.filter(a=>a.name.toLowerCase().includes(e))}),se=[{type:"selection"},{title:"名称",key:"name",ellipsis:{tooltip:!0},render:e=>C("div",{class:"file-name-cell",onClick:()=>e.is_dir&&K(e)},[C(w,{component:e.is_dir?Y:ee,size:20,class:e.is_dir?"folder-icon":"file-icon"}),C("span",{class:"file-name"},e.name)])},{title:"修改时间",key:"mtime",width:180,render:e=>J(e.mtime)},{title:"文件大小",key:"size",width:120,align:"right",render:e=>G(e.size)},{title:"操作",key:"actions",width:80,render:e=>e.is_dir?C(q,{size:"small",quaternary:!0,onClick:()=>Q(e)},{icon:()=>C(w,{component:U})}):null}],L=async(e="",a=1)=>{i.value=!0;try{const s=await qe.browse(e,a,R.value);_.value=s.entries,c.value=s.current_path,m.value=s.parent_path,g.value=s.total,v.value=s.page,k.replace({query:{...s.current_path?{root:s.current_path}:{},...a>1?{page:a.toString()}:{}}})}catch(s){f.error("加载目录失败"),console.error(s)}finally{i.value=!1}},K=e=>{e.is_dir&&(v.value=1,b.value="",y.value=[],L(e.path,1))},ne=()=>{m.value!==null&&(v.value=1,b.value="",y.value=[],L(m.value,1))},Z=e=>{v.value=1,b.value="",y.value=[],L(e,1)},ie=()=>{Z("")},le=e=>{v.value=e,y.value=[],L(c.value,e)},ce=e=>{y.value=e},Q=e=>{$.value=e.path,T.value=!0},ue=()=>{$.value=c.value,T.value=!0},de=()=>{f.success("任务已创建")},me=e=>({style:e.is_dir?"cursor: pointer;":"",onDblclick:()=>e.is_dir&&K(e)});return Re(()=>l.query,()=>{const e=l.query.root||"",a=parseInt(l.query.page)||1;(e!==c.value||a!==v.value)&&L(e,a)},{immediate:!1}),L(D.value,j.value),(e,a)=>{const s=Le("router-link");return n(),x("div",Xe,[u(r(Se),{class:"main-card glass-card"},{default:p(()=>[d("div",Ye,[d("div",We,[a[4]||(a[4]=d("h1",{class:"page-title"},"文件管理",-1)),u(r(w),{component:r(Ve),size:"18",class:"mode-icon"},null,8,["component"]),u(s,{to:"/filemanager/scan",class:"mode-link"},{default:p(()=>[...a[3]||(a[3]=[V("扫描模式",-1)])]),_:1})])]),d("div",et,[u(r(q),{quaternary:"",circle:"",size:"small",disabled:m.value===null&&!c.value,onClick:ne},{icon:p(()=>[u(r(w),{component:r(Ue)},null,8,["component"])]),_:1},8,["disabled"]),u(r(Je),{separator:"/"},{default:p(()=>[u(r(te),{onClick:ie},{default:p(()=>[...a[5]||(a[5]=[d("span",{class:"breadcrumb-root"},"根目录",-1)])]),_:1}),(n(!0),x(A,null,X(re.value,t=>(n(),P(r(te),{key:t.path,onClick:O=>Z(t.path)},{default:p(()=>[V(I(t.name),1)]),_:2},1032,["onClick"]))),128))]),_:1})]),d("div",tt,[d("div",at,[u(r(Fe),{value:b.value,"onUpdate:value":a[0]||(a[0]=t=>b.value=t),placeholder:"关键字过滤",clearable:"",class:"search-input"},{prefix:p(()=>[u(r(w),{component:r(Ne)},null,8,["component"])]),_:1},8,["value"])]),d("div",ot,[d("span",rt,"已选中 "+I(y.value.length)+" 个条目",1),u(r(q),{type:"primary",disabled:!c.value,onClick:ue},{icon:p(()=>[u(r(w),{component:r(U)},null,8,["component"])]),default:p(()=>[a[6]||(a[6]=V(" 创建任务 ",-1))]),_:1},8,["disabled"])])]),i.value&&_.value.length===0?(n(),P(Ae,{key:0,preset:"list",count:8})):r(B)?(n(),x(A,{key:1},[M.value.length>0?(n(),x("div",st,[(n(!0),x(A,null,X(M.value,t=>(n(),P(je,{key:t.path,clickable:"",class:"file-card",onClick:O=>t.is_dir?K(t):void 0},{suffix:p(()=>[d("div",mt,[t.is_dir?(n(),P(r(q),{key:0,size:"tiny",quaternary:"",circle:"",onClick:Ee(O=>Q(t),["stop"])},{icon:p(()=>[u(r(w),{component:r(U)},null,8,["component"])]),_:1},8,["onClick"])):N("",!0),t.is_dir?(n(),P(r(w),{key:1,component:r(De),class:"chevron-icon"},null,8,["component"])):N("",!0)])]),default:p(()=>[d("div",nt,[d("div",{class:$e(["file-icon-wrapper",{"is-folder":t.is_dir}])},[u(r(w),{component:t.is_dir?r(Y):r(ee),size:24},null,8,["component"])],2),d("div",it,[d("div",lt,I(t.name),1),d("div",ct,[t.size!==null?(n(),x("span",ut,I(G(t.size)),1)):N("",!0),t.mtime?(n(),x("span",dt,I(J(t.mtime)),1)):N("",!0)])])])]),_:2},1032,["onClick"]))),128))])):(n(),P(W,{key:1,title:"目录为空",description:"当前目录没有文件或文件夹"}))],64)):(n(),x(A,{key:2},[M.value.length>0?(n(),P(r(Ie),{key:0,columns:se,data:M.value,loading:i.value,"row-key":t=>t.path,"checked-row-keys":y.value,"row-props":me,"onUpdate:checkedRowKeys":ce},null,8,["data","loading","row-key","checked-row-keys"])):i.value?N("",!0):(n(),P(W,{key:1,title:"目录为空",description:"当前目录没有文件或文件夹"}))],64)),g.value>R.value?(n(),x("div",vt,[u(r(Me),{page:v.value,"onUpdate:page":[a[1]||(a[1]=t=>v.value=t),le],"page-size":R.value,"item-count":g.value},null,8,["page","page-size","item-count"])])):N("",!0)]),_:1}),u(Ke,{show:T.value,"onUpdate:show":a[2]||(a[2]=t=>T.value=t),"initial-scan-path":$.value,onSuccess:de},null,8,["show","initial-scan-path"])])}}}),St=Oe(pt,[["__scopeId","data-v-9989cd6c"]]);export{St as default};
