import{an as o,ao as s,ap as v,d as S,R,ar as q,aD as M,u as T,r as f,v as I,z as j,I as _,w as l,k as e,$ as L,o as d,j as a,W as z,D as k,p as W,q as Y,B as x,s as D,a as w,A,N as H,c as N,l as B,Y as J,y as Q,K as X,F as Z,aa as tt,x as et,_ as rt}from"./index-CxuZ4q-t.js";import{A as ot,f as at}from"./files-BfGyb9Th.js";const st=o("input-group",`
 display: inline-flex;
 width: 100%;
 flex-wrap: nowrap;
 vertical-align: bottom;
`,[s(">",[o("input",[s("&:not(:last-child)",`
 border-top-right-radius: 0!important;
 border-bottom-right-radius: 0!important;
 `),s("&:not(:first-child)",`
 border-top-left-radius: 0!important;
 border-bottom-left-radius: 0!important;
 margin-left: -1px!important;
 `)]),o("button",[s("&:not(:last-child)",`
 border-top-right-radius: 0!important;
 border-bottom-right-radius: 0!important;
 `,[v("state-border, border",`
 border-top-right-radius: 0!important;
 border-bottom-right-radius: 0!important;
 `)]),s("&:not(:first-child)",`
 border-top-left-radius: 0!important;
 border-bottom-left-radius: 0!important;
 `,[v("state-border, border",`
 border-top-left-radius: 0!important;
 border-bottom-left-radius: 0!important;
 `)])]),s("*",[s("&:not(:last-child)",`
 border-top-right-radius: 0!important;
 border-bottom-right-radius: 0!important;
 `,[s(">",[o("input",`
 border-top-right-radius: 0!important;
 border-bottom-right-radius: 0!important;
 `),o("base-selection",[o("base-selection-label",`
 border-top-right-radius: 0!important;
 border-bottom-right-radius: 0!important;
 `),o("base-selection-tags",`
 border-top-right-radius: 0!important;
 border-bottom-right-radius: 0!important;
 `),v("box-shadow, border, state-border",`
 border-top-right-radius: 0!important;
 border-bottom-right-radius: 0!important;
 `)])])]),s("&:not(:first-child)",`
 margin-left: -1px!important;
 border-top-left-radius: 0!important;
 border-bottom-left-radius: 0!important;
 `,[s(">",[o("input",`
 border-top-left-radius: 0!important;
 border-bottom-left-radius: 0!important;
 `),o("base-selection",[o("base-selection-label",`
 border-top-left-radius: 0!important;
 border-bottom-left-radius: 0!important;
 `),o("base-selection-tags",`
 border-top-left-radius: 0!important;
 border-bottom-left-radius: 0!important;
 `),v("box-shadow, border, state-border",`
 border-top-left-radius: 0!important;
 border-bottom-left-radius: 0!important;
 `)])])])])])]),lt={},it=S({name:"InputGroup",props:lt,setup(i){const{mergedClsPrefixRef:h}=q(i);return M("-input-group",st,h),{mergedClsPrefix:h}},render(){const{mergedClsPrefix:i}=this;return R("div",{class:`${i}-input-group`},this.$slots)}}),nt={class:"folder-list"},dt=["onClick"],ut={class:"folder-name"},pt=S({__name:"FolderBrowser",props:{modelValue:{default:""},show:{type:Boolean,default:!1},title:{default:"选择文件夹"}},emits:["update:modelValue","update:show","select"],setup(i,{emit:h}){const y=i,u=h,U=T(),p=f(!1),m=f(""),g=f(null),P=f([]),c=f(""),C=I({get:()=>y.modelValue,set:r=>u("update:modelValue",r)}),b=async(r="")=>{p.value=!0;try{const t=await at.browse(r);m.value=t.current_path,g.value=t.parent_path,P.value=t.entries,c.value=t.current_path}catch(t){U.error("加载目录失败"),console.error(t)}finally{p.value=!1}},$=r=>{r.is_dir&&b(r.path)},E=()=>{g.value!==null&&b(g.value)},G=()=>{b(m.value)},V=()=>{c.value&&b(c.value)},K=()=>{C.value=m.value,u("select",m.value),u("update:show",!1)},O=()=>{u("update:show",!1)},F=I(()=>P.value.filter(r=>r.is_dir));return j(()=>y.show,r=>{r&&b(y.modelValue||"")},{immediate:!0}),(r,t)=>(d(),_(e(L),{show:i.show,"mask-closable":!0,"onUpdate:show":t[1]||(t[1]=n=>u("update:show",n))},{default:l(()=>[a(e(et),{title:i.title,size:"small",class:"folder-browser-modal",bordered:!1,closable:"",onClose:O},{"header-extra":l(()=>[a(e(x),{quaternary:"",circle:"",size:"small",loading:p.value,onClick:G},{icon:l(()=>[a(e(B),{component:e(tt)},null,8,["component"])]),_:1},8,["loading"])]),default:l(()=>[a(e(z),{vertical:""},{default:l(()=>[a(e(it),null,{default:l(()=>[a(e(W),{value:c.value,"onUpdate:value":t[0]||(t[0]=n=>c.value=n),placeholder:"输入路径",onKeyup:Y(V,["enter"])},null,8,["value"]),a(e(x),{type:"primary",onClick:V},{default:l(()=>[...t[2]||(t[2]=[D("跳转",-1)])]),_:1})]),_:1}),C.value?(d(),_(e(z),{key:0},{default:l(()=>[w("span",null,"已选择: "+A(C.value),1)]),_:1})):k("",!0),a(e(H),{show:p.value},{default:l(()=>[w("div",nt,[g.value!==null?(d(),N("div",{key:0,class:"folder-item",onClick:E},[a(e(B),{component:e(ot),size:"20"},null,8,["component"]),t[3]||(t[3]=w("span",{class:"folder-name"},"..",-1))])):k("",!0),F.value.length===0&&!p.value?(d(),_(e(J),{key:1,description:"目录为空"})):k("",!0),(d(!0),N(Z,null,Q(F.value,n=>(d(),N("div",{key:n.path,class:"folder-item",onClick:mt=>$(n)},[a(e(B),{component:e(X),size:"20"},null,8,["component"]),w("span",ut,A(n.name),1)],8,dt))),128))])]),_:1},8,["show"]),a(e(x),{type:"primary",block:"",disabled:!m.value,onClick:K},{default:l(()=>[...t[4]||(t[4]=[D(" 选择此文件夹 ",-1)])]),_:1},8,["disabled"])]),_:1})]),_:1},8,["title"])]),_:1},8,["show"]))}}),ft=rt(pt,[["__scopeId","data-v-98a2d804"]]);export{ft as F,it as N};
