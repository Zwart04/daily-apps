let csrf='';
export const setCsrf=value=>{csrf=value||'';};
export async function api(path,method='GET',payload) {
 const response=await fetch('/api'+path,{method,credentials:'same-origin',headers:{'Content-Type':'application/json',...(csrf?{'X-CSRF-Token':csrf}:{})},body:payload===undefined?undefined:JSON.stringify(payload)});
 let data;try{data=await response.json();}catch{throw new Error('Server tidak mengirim response JSON.');}
 if(!response.ok) {const error=new Error(data.error||'Request gagal ('+response.status+').');error.status=response.status;if(response.status===401&&!path.startsWith('/auth/'))window.dispatchEvent(new Event('session-expired'));throw error;}
 if(data.csrf)setCsrf(data.csrf);return data;
}
export function download(name,content,type='text/plain') {const url=URL.createObjectURL(new Blob([content],{type}));const a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{a.remove();URL.revokeObjectURL(url);},30000);}
export const money=(value,currency='IDR')=>new Intl.NumberFormat('id-ID',{style:'currency',currency,maximumFractionDigits:currency==='IDR'?0:2}).format((Number(value)||0)/100);
export const date=value=>value?new Date(value).toLocaleDateString('id-ID',{day:'numeric',month:'short',year:'numeric'}):'—';
export const dateTime=value=>value?new Date(value).toLocaleString('id-ID',{dateStyle:'medium',timeStyle:'short'}):'—';
export const localDate=(value=new Date())=>{const date=value instanceof Date?value:new Date(value);return new Date(date.getTime()-date.getTimezoneOffset()*60000).toISOString().slice(0,10);};
export const localTime=value=>value?new Date(new Date(value).getTime()-new Date(value).getTimezoneOffset()*60000).toISOString().slice(0,16):'';
export function csv(records,fields) {const safe=value=>{let s=typeof value==='object'?JSON.stringify(value):String(value??'');if(typeof value==='string'&&/^[=+@\-\t\r]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';};return '\uFEFF'+[fields.map(safe).join(','),...records.map(r=>fields.map(f=>safe(r[f]??r.data?.[f])).join(','))].join('\r\n');}
export const labels={active:'Aktif',archived:'Arsip',todo:'Belum dimulai',doing:'Dikerjakan',done:'Selesai',draft:'Draft',confirmed:'Dikonfirmasi',paid:'Dibayar',unpaid:'Belum dibayar',shipped:'Dikirim',completed:'Selesai',cancelled:'Dibatalkan',pending:'Menunggu',posted:'Diposting',published:'Diterbitkan',closed:'Ditutup',open:'Terbuka',scheduled:'Terjadwal',checked_in:'Check-in',submitted:'Dikirim',graded:'Dinilai',sealed:'Terkunci',in_progress:'Dikerjakan',review:'Review',planning:'Perencanaan',booked:'Dipesan',acknowledged:'Diketahui',resolved:'Diselesaikan',passed:'Lulus',failed:'Gagal'};
export const actionLabels={'confirm-order':'Konfirmasi & alokasikan stok','invoice-order':'Buat invoice','pay-order':'Catat pembayaran diterima','ship-order':'Catat pengiriman','complete-order':'Tandai diterima pelanggan','cancel-order':'Batalkan pesanan','post-stock':'Posting mutasi stok','booking-job':'Buat pekerjaan','appointment-encounter':'Mulai kunjungan'};

actionLabels["publish-form"]="Buat tautan form";
