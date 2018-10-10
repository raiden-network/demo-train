let nodeDiameter = 30;
let graph;
let noiseIncrement= 0.003
let nodeJitter = 70
let backgroundColor = 200
let qrImage;

let graphPosX = 400
let graphPosY = 100
let graphScale = 1.
let qrSize = 300;

let providerEndpoint = 'http://localhost:5000/api/1/provider/current'
let pathEndpoint = 'http://localhost:5000/api/1/path/current'
let currentProvider;
let currentPath = [];


let SENDER_ADDRESS = "0x00D384EF74575E97884215e9f39142228c7ACfa8"
let RECEIVER_1_ADDRESS = "0x002857f3a3BEa9DC0301D6DCf573692720f88B5a"
let RECEIVER_2_ADDRESS = "0x0087b32F69DB0b92cA5F268b499017DC5ca6EBFA"
let RECEIVER_3_ADDRESS = "0x00b349E94436A3873b0a8b76eCe15d5f131F3128"
let RECEIVER_4_ADDRESS = "0x0006CaA8eE29a6bbe66b74bf77b30371816AFD7c"
let RECEIVER_5_ADDRESS = "0x006daf7986d23b700A5361830B7961F45D252F8C"
let RECEIVER_6_ADDRESS = "0x00a614cf3C67CF541c633728224Ca0d5EC82f1dE"
let RECEIVER_7_ADDRESS = "0x00C68910D9C719a5612790343862bcdF49d6a29A"
let RECEIVER_8_ADDRESS = "0x00673b5556Db5Fe0DdDB0875bF565a3a4AE51Dcb"



class Graph {

	constructor () {
		this.nodeArray = [];
		this.edgeArray = [];
		this.edges = createNumberDict();
		this.nodes = createNumberDict();
	}

	makeEdge (address_from, address_to) {
		// FIXME assumes that this.nodes exists !
		let fromNodeIndex = this.nodes.get(address_from)
		let toNodeIndex = this.nodes.get(address_to);
		if ((fromNodeIndex !== null) && (toNodeIndex !== null)) {
			let fromNode = this.nodeArray[fromNodeIndex]
			let toNode = this.nodeArray[toNodeIndex]
			let edge = new Edge(fromNode, toNode);
			let index = this.edgeArray.push(edge) - 1 
			this.edges.set(fromNode.address + '$' + toNode.address, index);
			this.edges.set(toNode.address + '$' + fromNode.address, index);
		}
	}

	addNode (node) {
		this.nodeArray.push(node)
		this.nodes.set(node.address, this.nodeArray.length-1);
	}


	drawNodes(highlighted=null) {
		for (var i = 0; i < this.nodeArray.length ; i++) {
			var node = this.nodeArray[i]
			node.draw()
		}
	}
	drawEdges(highlighted=null) {
		var highlightedEdges;
		if (highlighted !== null) {
			highlightedEdges = new Set(highlighted);
		} else {
			highlightedEdges = new Set([]);
		}

		for (var i = 0; i < this.edgeArray.length ; i++) {
			var edge = this.edgeArray[i];
			if (highlightedEdges.has(edge)) {
				edge.draw(true)
			} else {
				edge.draw(false);
			}
		}
	}

	//  TODO Path drawing isn't working as expected
	draw (path=null) {
		var pathEdges;
		if (path !== null) {
			pathEdges = this.getPathEdges(path);
		}
		this.drawEdges(pathEdges);
		this.drawNodes();	
	}

	getPathEdges(pathArray) {
		var pathEdges = [];
		for (var i = 0; i < pathArray.length - 1 ; i++) {
			let fromAddress = pathArray[i];
			let toAddress = pathArray[i+1];
			let edgeIndex = this.edges.get(fromAddress + '$' + toAddress);
			// let edgeIndex = this.edges.get(toAddress + '$' + fromAddress);
			if (edgeIndex !== null) {
				let edge = this.edgeArray[edgeIndex];
				pathEdges.push(edge);
			}
		}
		return pathEdges;
	}

	advance() {
		for (var i = 0; i < this.nodeArray.length ; i++) {
			var node = this.nodeArray[i]
			node.advanceOffsets();
		}
	}
}

class Edge {
	constructor (fromNode, toNode) {
		this.fromNode = fromNode;
		this.toNode = toNode;

	}

	draw (highlight=false) {
		push();
		strokeWeight(4);
		if (highlight == true) {
			stroke(10,150,10);
			line(this.fromNode.xPos, this.fromNode.yPos, this.toNode.xPos, this.toNode.yPos);
		} else {
			stroke(255)
			line(this.fromNode.xPos, this.fromNode.yPos, this.toNode.xPos, this.toNode.yPos);
		} 
		pop();
	}
}

class Node {
	constructor (address, xPos, yPos) {
		this.address = address;
		this._xPos = xPos;
		this._yPos = yPos;
		//  TODO assign random int	
		this.xNoiseOffset = int(random(0, 2**16));
		this.yNoiseOffset = int(random(0, 2**16));
	}
	
	get xPos (){
		return this._xPos + noise(this.xNoiseOffset) * nodeJitter
	}	

	get yPos (){
		return this._yPos + noise(this.yNoiseOffset) * nodeJitter
	}

	draw () {
		ellipse(this.xPos, this.yPos,nodeDiameter, nodeDiameter);
	}

	advanceOffsets() {
		this.xNoiseOffset += noiseIncrement;
		this.yNoiseOffset += noiseIncrement;
	}
}

class Provider {
	constructor (address, identifier){
		this.address = address;
		this.identifier = identifier;
	}

}
function getRelativePos(xRel, yRel) {
	// TODO scale values from float(0) to float(100)
	// to pixel positions based on the window width and height
}



function fetchImage() {
	qrImg = loadImage("../../current_barcode.svg");
}



function queryProvider () {
	httpGet(providerEndpoint, 'json', false, onProvider)
}

function queryPath() {
	httpGet(pathEndpoint, 'json', false, onPath)
}


function onProvider(data) {
	newProvider = new Provider(data.address, data.identifier);
	if (newProvider !== currentProvider){
		currentProvider = newProvider;
		onNewProvider();
	}
}

function onNewProvider(){
	fetchImage()
	queryPath()
}

function onPath(data) {
	currentPath = data
}

function addNode(graph, node, xRel, yRel) {
	// TODO s
	graph.addNode(node, graphPosX + xRel * graphScale, graphPosY + yRel * graphScale)
}


function setup() {
	createCanvas(windowWidth, windowHeight);
	background(backgroundColor);

	strokeCap(ROUND);
	strokeJoin(ROUND);
	// stroke(255);
	noStroke();

	graph = new Graph();



	addNode(graph, new Node(SENDER_ADDRESS, 400, 100));
	addNode(graph, new Node(RECEIVER_1_ADDRESS, 400,200));

	addNode(graph, new Node(RECEIVER_2_ADDRESS, 400, 300));
	addNode(graph, new Node(RECEIVER_5_ADDRESS, 200,300));
	addNode(graph, new Node(RECEIVER_8_ADDRESS, 600,300));


	addNode(graph, new Node(RECEIVER_3_ADDRESS, 400,400));
	addNode(graph, new Node(RECEIVER_4_ADDRESS, 400,500));

	addNode(graph, new Node(RECEIVER_6_ADDRESS, 200, 400));
	addNode(graph, new Node(RECEIVER_7_ADDRESS, 200, 500));
	

	graph.makeEdge(SENDER_ADDRESS, RECEIVER_1_ADDRESS);
	graph.makeEdge(RECEIVER_1_ADDRESS, RECEIVER_2_ADDRESS);
	graph.makeEdge(RECEIVER_1_ADDRESS, RECEIVER_5_ADDRESS);
	graph.makeEdge(RECEIVER_1_ADDRESS, RECEIVER_8_ADDRESS);
	graph.makeEdge(RECEIVER_5_ADDRESS, RECEIVER_6_ADDRESS);
	graph.makeEdge(RECEIVER_6_ADDRESS, RECEIVER_7_ADDRESS);
	graph.makeEdge(RECEIVER_2_ADDRESS, RECEIVER_3_ADDRESS);
	graph.makeEdge(RECEIVER_3_ADDRESS, RECEIVER_4_ADDRESS);

	fetchImage();
	setInterval(queryProvider, 500);
}


function draw() {
	background(backgroundColor);
	graph.draw(currentPath);
	graph.advance();

	// Can this be done not everytime in the draw loop?
	qrImg.resize(qrSize,0);
	image(qrImg, 900, 100);

}
