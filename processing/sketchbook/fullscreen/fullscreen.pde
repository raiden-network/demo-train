int x = 0;

void setup(){
   fullScreen(P2D);
   background(0);
   fill(100);
   stroke(100);
}

void draw(){
  rect(x, height*0.2, 1, height*0.6); 
  x = x + 2;
  ellipse(mouseX,mouseY,20,20);
  
}

void mouseClicked(){
  String posi = "x: " + mouseX + "\ny: " + mouseY;
  text(posi,mouseX,mouseY);

}
