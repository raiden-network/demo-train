import processing.net.*; 
Client myClient;
int i = 0;
void setup() { 
  size(200, 200); 
  /* Connect to the local machine at port 5204
   *  (or whichever port you choose to run the
   *  server on).
   * This example will not run if you haven't
   *  previously started a server on this port.
   */
  myClient = new Client(this, "127.0.0.1", 5205); 
} 

void draw() { 
  i++;
  myClient.write("raiden train rolls in"+i); // send whatever you need to send here
  println(myClient.readChar());
} 
