void setup(){
   fullScreen(P2D);
   background(0);
   fill(100);
   stroke(100);
}

void draw(){
  
}

void mouseClicked(){
  String posi = "x: " + mouseX + "\ny: " + mouseY;
  text(posi,mouseX,mouseY);

}
