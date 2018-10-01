import http.requests.*;


int requestInterval = 100;
int counter = requestInterval;

public class Provider {
      //20 byte hex string
      public String address;
      // 32 bit integer
      public int identifier;
      
      public Provider(JSONObject json){
          this.address = json.getString("address");
          this.identifier = json.getInt("identifier");


      };
      
      public int hash() {
        // This will also include the indentifier in the hash we probably don't want this,
        // but we can come up with a more clever hashing scheme later
        
        String concatString = this.address + hex(this.identifier);
        //return the hashcode of the string and then hash to an int value
        return Long.hashCode(concatString.hashCode());
      };
}

public void setup() 
{
  size(400,400);
  smooth();
}


Provider currentProvider;

public void draw()
{
  if (counter == requestInterval) {
    currentProvider = queryProvider();
    counter = 0;
  }
  counter++;
  color bgColor = currentProvider.hash();
  background(bgColor);
}

public Provider queryProvider() {
    
  GetRequest get = new GetRequest("http://localhost:5000/api/1/provider/current");
  get.send(); // program will wait untill the request is completed
  println("response: " + get.getContent());

  JSONObject response = parseJSONObject(get.getContent());
  return new Provider(response);
}
