import processing.net.*;
Client pyCli;

int last=0;
int current=0;
int average=-1;
int xx = 0;

void setup(){
  size(600,600);
  background(0);
  fill(255);
  stroke(255);
  //pyCli = new Client(this, "127.0.0.1", 5203);
  
}

void draw(){
  //println(millis()); 
}

void keyPressed(){
 println(keyCode);
 xx+=5;
 if(keyCode==32){
   int now = millis();
   current=now-last;
   last=now;
   println(current);
   
   if(average==-1){
    average=current; 
   }
   
   average=(2*average+current)/3;
   println(average);
   stroke(255);
   point(xx,average/10);
   stroke(255,0,0);
   point(xx,current/10);
 }
}
