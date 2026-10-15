const fs=require('fs'),vm=require('vm'),assert=require('assert');
const elements=new Map();
const defaults={surcharge:37,income:0,saving:0,relief:0,group:'income',metric:'burden',familySize:4,paymentPeriod:12,proposalBenefit:415,dcMW:100,dcUtil:80,dcRate:10,dcShare:20};
function element(id){if(!elements.has(id))elements.set(id,{value:String(defaults[id]??0),innerHTML:'',textContent:'',setAttribute(){},addEventListener(){}});return elements.get(id)}
const context={document:{getElementById:element,querySelectorAll:()=>[]},window:{},requestAnimationFrame:f=>f(),cancelAnimationFrame(){},console};
vm.createContext(context);
const html=fs.readFileSync('outputs/interactive_presentation_graphs.html','utf8');
vm.runInContext(html.match(/<script>([\s\S]*)<\/script>/)[1],context);
for(const [price,gap,high] of [[0,749.2499402442835,314224.42981559335],[14,826.0978209597216,331241.0514722267],[37,954.5829706553144,358429.8368707533]]){
 element('surcharge').value=String(price);vm.runInContext('render()',context);const r=context.window.dashboardResult.total;
 assert(Math.abs(r.gap/1e6-gap)<1e-6);assert(Math.abs(r.high-high)<1e-6);
}
const before=context.window.dashboardResult.total;
element('saving').value='40';element('relief').value='1500';element('income').value='40';element('group').value='fuel';element('metric').value='gap';vm.runInContext('render()',context);
const after=context.window.dashboardResult.total;assert(after.gap<before.gap&&after.high<before.high&&after.c/after.i<before.c/before.i);
for(const id of ['burdenChart','gapChart','distributionChart','rankChart'])assert(!/NaN|Infinity/.test(element(id).innerHTML),id);
assert(Math.abs(after.bins.reduce((a,b)=>a+b,0)-after.n)<1e-6);
for(const metric of ['burden','gap','total']){element('metric').value=metric;vm.runInContext('render()',context);assert(element('rankChart').innerHTML.includes('<rect'))}
assert(!/<script[^>]+src=|<link[^>]+href=/.test(html));
const payment=context.window.paymentResult;
assert.equal(payment.line,33000);assert.equal(payment.kwh,700800000);assert.equal(payment.utility,70080000);assert.equal(payment.tax,7708800);
assert.equal(payment.share,.2);assert.equal(payment.period,12);
element('saving').value='0';element('relief').value='0';vm.runInContext('render()',context);
const p=context.window.paymentResult;
const benefitUsed=(p.noRelief.groups[0].c-p.participant.groups[0].c)/p.noRelief.groups[0].n;
assert(benefitUsed>400&&benefitUsed<=415+.00001); // Some cells have bills below the benefit cap.
assert.equal(p.noRelief.groups[2].c,p.participant.groups[2].c);
element('familySize').value='1';element('paymentPeriod').value='1';element('dcShare').value='25';vm.runInContext('renderPayments(state())',context);
assert.equal(context.window.paymentResult.line,15960);assert.equal(context.window.paymentResult.period,1);assert.equal(context.window.paymentResult.share,.25);
for(const id of ['paymentRows','dcRows','housePaymentChart','dcPaymentChart'])assert(!/NaN|Infinity/.test(element(id).innerHTML),id);
console.log('PASS: notebook benchmarks, threshold counts, policy response, chart variables, finite SVG coordinates, distribution totals, offline dependencies.');
