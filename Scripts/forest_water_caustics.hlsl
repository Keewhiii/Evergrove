// Gentle standing-water motion. Irregular rings remain local to physical contact.
float shallow=pow(saturate(Depth),2.4);
float2 p=Position.xy;
float swell=0.5+0.5*sin(p.x*0.006+p.y*0.004+Clock*0.22+0.45*sin(p.y*0.008-Clock*0.17));
float3 blue=lerp(float3(0.018,0.105,0.23),float3(0.045,0.30,0.38),shallow);
blue*=0.93+0.07*swell;
// Soft, broken reflection strokes drift slowly, without tessellated/cellular ripples.
float lane=pow(saturate(0.5+0.5*sin(p.y*0.052+p.x*0.009+Clock*0.36+sin(p.x*0.014-Clock*0.12))),24.0);
float breakup=pow(saturate(0.5+0.5*sin(p.x*0.036+sin(p.y*0.012)+Clock*0.15)),7.0);
float reflection=lane*breakup*(0.35+0.65*shallow);
blue+=reflection*float3(0.055,0.10,0.11);
// Restrained shore wash: narrow moving highlight only in the shallow margin.
float shore=smoothstep(0.86,0.94,Depth)*(1.0-smoothstep(0.97,1.03,Depth));
float wash=0.5+0.5*sin(Depth*46.0-Clock*0.85+sin(p.x*0.01+p.y*0.012));
blue+=shore*pow(wash,8.0)*pow(saturate(0.5+0.5*sin(p.x*0.012+p.y*0.015-Clock*0.15)),2.0)*float3(0.025,0.045,0.035);
float radius=length(p-Contact.xy);
float envelope=Interaction*exp(-radius/95.0)*(1.0-smoothstep(90.0,220.0,radius));
float angle=atan2(p.y-Contact.y,p.x-Contact.x);
float ring=pow(saturate(0.5+0.5*sin(radius*0.17-Clock*7.0+0.35*sin(angle*4.0+Clock))),10.0);
return blue+ring*envelope*float3(0.09,0.20,0.24);
