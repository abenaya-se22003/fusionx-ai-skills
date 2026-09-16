/* Content-driven FusionX URS generator. Based on the proven docx-js mechanics
   from the Debit Charges V0.1 v3 build; it contains no customer/UAT artifacts. */
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, TableOfContents,
  Header, Footer, SimpleField, ExternalHyperlink, ImageRun, AlignmentType, HeadingLevel,
  LevelFormat, LevelSuffix, WidthType, BorderStyle, ShadingType, VerticalAlign,
  TableLayoutType, PageBreak, convertMillimetersToTwip,
} = require("docx");

const CANDARA="Candara", HBLUE="2F5496", COVERBLUE="0070C0", LIGHTBLUE="D5DCE4", NAVY="002060";
const args=process.argv.slice(2); const input=args[0]; const i=args.indexOf("--output");
if(!input || i<0 || !args[i+1]) throw new Error("Usage: node build.js <draft.json> --output <docx>");
const data=JSON.parse(fs.readFileSync(input,"utf8")); const output=path.resolve(args[i+1]);
const run=(text,o={})=>new TextRun({text:String(text??""),font:CANDARA,size:22,...o});
const bold=(text,o={})=>run(text,{bold:true,...o});
const border={style:BorderStyle.SINGLE,size:4,color:"BFBFBF"};
const numbering={config:[
 {reference:"main",levels:[
  {level:0,format:LevelFormat.DECIMAL,text:"%1.",alignment:AlignmentType.START,suffix:LevelSuffix.TAB,style:{paragraph:{indent:{left:720,hanging:504}},run:{font:CANDARA}}},
  {level:1,format:LevelFormat.DECIMAL,text:"%1.%2.",alignment:AlignmentType.START,suffix:LevelSuffix.TAB,style:{paragraph:{indent:{left:1080,hanging:504}},run:{font:CANDARA}}},
  {level:2,format:LevelFormat.DECIMAL,text:"%1.%2.%3.",alignment:AlignmentType.START,suffix:LevelSuffix.TAB,style:{paragraph:{indent:{left:720,hanging:720}},run:{font:CANDARA}}},
  {level:3,format:LevelFormat.DECIMAL,text:"%1.%2.%3.%4.",alignment:AlignmentType.START,suffix:LevelSuffix.TAB,style:{paragraph:{indent:{left:900,hanging:900}},run:{font:CANDARA}}}]},
 {reference:"second",levels:[
  {level:0,start:7,format:LevelFormat.DECIMAL,text:"%1.",alignment:AlignmentType.START,suffix:LevelSuffix.TAB,style:{paragraph:{indent:{left:720,hanging:504}},run:{font:CANDARA}}},
  {level:1,format:LevelFormat.DECIMAL,text:"%1.%2.",alignment:AlignmentType.START,suffix:LevelSuffix.TAB,style:{paragraph:{indent:{left:1080,hanging:504}},run:{font:CANDARA}}}]},
 {reference:"bullets",levels:[{level:0,format:LevelFormat.BULLET,text:"•",alignment:AlignmentType.START,suffix:LevelSuffix.TAB,style:{paragraph:{indent:{left:360,hanging:360}},run:{font:CANDARA}}}]}
]};
const h1=(text,second=false,breakBefore=false)=>new Paragraph({heading:HeadingLevel.HEADING_1,numbering:{reference:second?"second":"main",level:0},pageBreakBefore:breakBefore,spacing:{before:240,after:0},children:[run(text,{size:32,color:HBLUE})]});
const h2=(text,second=false)=>new Paragraph({heading:HeadingLevel.HEADING_2,numbering:{reference:second?"second":"main",level:1},spacing:{before:40,after:0},children:[run(text,{size:26,color:HBLUE})]});
const body=(text)=>new Paragraph({spacing:{after:120,line:276,lineRule:"auto"},children:[run(text)]});
const bullet=(text)=>new Paragraph({numbering:{reference:"bullets",level:0},spacing:{after:120,line:276,lineRule:"auto"},children:[run(text)]});
const blank=()=>new Paragraph({spacing:{after:200,line:276,lineRule:"auto"}});
function cell(value,shade=false){return new TableCell({shading:shade?{type:ShadingType.CLEAR,fill:LIGHTBLUE}:undefined,verticalAlign:VerticalAlign.CENTER,children:[new Paragraph({children:[run(value)]})]});}
function grid(headers,rows,dark=false){return new Table({width:{size:9026,type:WidthType.DXA},layout:TableLayoutType.FIXED,style:dark?"GridTable4-Accent3":"TableGrid",borders:dark?undefined:{top:border,bottom:border,left:border,right:border,insideHorizontal:border,insideVertical:border},rows:[new TableRow({children:headers.map(x=>dark?cell(x):cell(x,true))}),...rows.map(row=>new TableRow({children:headers.map((_,n)=>cell(row[n]??""))}))]});}
function story(story){const rows=[["User & Function",story.user_function],["Action",story.action],["Result",story.result],["Pre-Conditions",story.preconditions],["Trigger",story.trigger],["Expected",story.expected]];return new Table({width:{size:9026,type:WidthType.DXA},layout:TableLayoutType.FIXED,style:"TableGrid",borders:{top:border,bottom:border,left:border,right:border,insideHorizontal:border,insideVertical:border},rows:rows.map(([label,value])=>new TableRow({children:[new TableCell({shading:{type:ShadingType.CLEAR,fill:LIGHTBLUE},children:[new Paragraph({numbering:{reference:"main",level:2},children:[bold(label)]})]}),new TableCell({children:[new Paragraph({numbering:{reference:"main",level:3},spacing:{after:120,line:276,lineRule:"auto"},children:[run(value||"")]})]})]}))});}
const title=data.title||"FusionX User Requirement Specification";
const metadata=[["Document Version",data.version||"0.1"],["Release Date",data.release_date||""],["Number of Pages","[updated by Word]"]];
const cover=[blank(),blank(),blank(),new Paragraph({border:{bottom:{style:BorderStyle.SINGLE,size:6,space:1,color:"BFBFBF"}},children:[run(title,{size:44,color:COVERBLUE})]}),body("User Requirement Specification"),grid(["Document information","Value"],metadata),blank(),blank(),blank(),new Paragraph({children:[run("LOLC Technologies",{bold:true,size:30,color:"1A0DAB"})]})];
const front=[new Paragraph({heading:HeadingLevel.HEADING_1,pageBreakBefore:true,children:[run("Table of Content",{size:32,color:HBLUE})]}),new TableOfContents("Table of Content",{hyperlink:true,headingStyleRange:"1-3"}),new Paragraph({heading:HeadingLevel.HEADING_1,children:[run("List of Figures",{size:32,color:HBLUE})]}),new TableOfContents("List of Figures",{hyperlink:true,captionLabelIncludingNumbers:"Figure"}),new Paragraph({heading:HeadingLevel.HEADING_1,children:[run("List of Tables",{size:32,color:HBLUE})]}),new TableOfContents("List of Tables",{hyperlink:true,captionLabelIncludingNumbers:"Table"}),blank()];
const children=[...cover,...front];
children.push(h1("Document Control",false)); children.push(h2("Document Information")); children.push(grid(["Field","Value"],[["Drafted By",data.drafted_by||""],["Reviewed By",data.reviewed_by||""],["Client Name",data.client||"LOLC Technologies Pvt LTD"],["Related Jira",data.jira||"[TO BE CONFIRMED]"]]));
children.push(blank(),h2("Assumptions")); (data.assumptions||[]).forEach(x=>children.push(bullet(x)));
children.push(blank(),h1("Open Questions")); children.push(grid(["ID","Question","Owner","Status"],data.open_questions||[],true));
children.push(blank(),h1("Overview/Project Description")); children.push(body(data.overview||"[To be completed]"));
children.push(h1("Flow Chart")); children.push(body(data.flow_chart||"[To be completed]"));
children.push(h1("Scope")); children.push(h2("What is in scope")); (data.in_scope||[]).forEach(x=>children.push(bullet(x))); children.push(blank(),h2("What is out of scope")); (data.out_of_scope||[]).forEach(x=>children.push(bullet(x)));
children.push(blank(),h1("Epic: Narrative and Statement")); children.push(body(data.epic||"[To be completed]"));
children.push(h1("Features/Stories")); (data.stories||[]).forEach((s,n)=>{children.push(h2(s.title||`Story ${String(n+1).padStart(2,"0")}`));children.push(story(s));});
children.push(blank(),h1("Data Dictionary",true)); children.push(grid(["Feature","Field Name","Data Type","Source / Retrieve From","Constraint / Description","Sample Data","Data Validation","Max Length"],data.data_dictionary||[],true));
children.push(blank(),h1("E2E Impact Identification Table",true)); children.push(grid(["Area","Impact","Details"],data.e2e_impact||[],true));
children.push(blank(),h1("Diagrams and Examples",true)); children.push(body(data.diagrams||"[To be completed]"));
children.push(h1("Annexure",true)); if(data.annexure){children.push(new Paragraph({children:[new ExternalHyperlink({link:data.annexure,children:[run(data.annexure,{style:"Hyperlink"})]})]}));} else children.push(body("[To be completed]"));
children.push(h1("Test Scenarios",true)); (data.test_scenarios||[]).forEach(row=>children.push(bullet(Array.isArray(row)?`${row[0]}: ${row[1]} → ${row[2]}`:row)));
const header=new Header({children:[new Paragraph({alignment:AlignmentType.CENTER,border:{bottom:{style:BorderStyle.SINGLE,size:6,space:1,color:"BFBFBF"}},children:[run("Proprietary and Confidential",{color:"BFBFBF",size:18})]})]});
const footer=new Footer({children:[new Paragraph({children:[run("URS "),new TextRun({font:CANDARA,size:18,children:[new SimpleField("DOCPROPERTY Title",title)]})]}),new Paragraph({alignment:AlignmentType.RIGHT,children:[run("Page "),new TextRun({font:CANDARA,size:18,children:[new SimpleField("PAGE","1")]}),run(" | "),new TextRun({font:CANDARA,size:18,children:[new SimpleField("NUMPAGES","1")]})]})]});
const doc=new Document({title,numbering,styles:{default:{document:{run:{font:CANDARA,size:22}},heading1:{run:{font:CANDARA,size:32,color:HBLUE}},heading2:{run:{font:CANDARA,size:26,color:HBLUE}}}},sections:[{properties:{page:{size:{width:convertMillimetersToTwip(210),height:convertMillimetersToTwip(297)},margin:{top:1440,bottom:1440,left:1440,right:1440}}},headers:{default:header},footers:{default:footer},children}]});
Packer.toBuffer(doc).then(buffer=>{fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,buffer);console.log(`written: ${output}`)});
