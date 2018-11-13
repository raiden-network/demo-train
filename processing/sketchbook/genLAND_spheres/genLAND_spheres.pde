
Kreeis[] punkte = new Kreeis[500];
float zoom;
float rot;

void setup(){
  size(1400,800,P3D);
  drawSpheres();
}
void drawSpheres(){
  fill(random(0,255),random(0,255),random(0,255),245);
  zoom = random(-20,20);
  rot = random(-0.75,-0.4);
  stroke(random(0,255),random(10,50));
  for(int i = 0; i < punkte.length; i++){
    punkte[i] = new Kreeis(int(random(width)),int(random(height)));
  }

  translate(0,0,zoom);
  rotateY(rot);
  println(rot);
  background(0);
  
  for(Kreeis bew : punkte){
    pushMatrix();
    translate(bew.x,bew.y,bew.z);
    sphere(random(50));
    fill(random(250,255),random(250,255),random(250,255),random(0,55));
    popMatrix();
  } 
}


void draw(){
 // translate(0,0,zoom);
 // rotateY(rot);
 // background(0);
 // for(Kreeis bew : punkte){
 //   pushMatrix();
 //   translate(bew.x,bew.y,bew.z);
 //   sphere(random(50));
 //   fill(random(250,255),random(50,155),random(250,255),random(0,55));
 //   popMatrix();
 //   if (mouseX > bew.x  -bew.ran && mouseX < bew.x +bew.ran &&  mouseY > bew.y -bew.ran &&  mouseY < bew.y +bew.ran){
 //     //println(bew.x);
 //     bew.x = mouseX;
 //     bew.y = mouseY;
 //   }
 //}
}

void mouseDragged(){
 rot += (pmouseX - mouseX)/10.;
 println(rot);
 zoom += pmouseY-mouseY;
}

void keyPressed(){
  drawSpheres();  
}

class Kreeis{
  int x;
  int y;
  int z;
  int r;
  int ran = 5;
  
  Kreeis(int xx, int yy){
    this.x = xx;
    this.y = yy;
  }
}
