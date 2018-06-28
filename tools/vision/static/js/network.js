(function() {
    var container = document.getElementById('networkview');
    fetch('/network').then((res) => {
        window.networkIds = [];        
        res.json().then((data) => {
            var options = {
                nodes: {
                    shape: 'dot',
                    size: 30,
                    font: {
                        size: 22,
                        color: '#fffffff'
                    },
                    borderWidth: 2
                },
                edges: {
                    width: 2
                }
            };	

            data.edges.push({'from': 'plebbot3465', 'to': 'plebbot6525'});
            data.edges.push({'from': 'plebbot3465', 'to': 'plebbot6197'});            

            dataNodes = new vis.DataSet(data.nodes)
            dataEdges = new vis.DataSet(data.edges)
                        
            vData = {nodes: dataNodes, edges: dataEdges}

            for (var i = 0; i < data.nodes.length; i++) {
                node = data.nodes[i];
                window.networkIds.push(node.id);
            }

            network = new vis.Network(container, vData, options);

            document.addEventListener('keyup', (event) => {
                const keyName = event.key;
              
                // As the user releases the Ctrl key, the key is no longer active,
                // so event.ctrlKey is false.
                if (keyName === 'Enter') {
                    dataNodes.update({id:'plebbot5542', label:'plebbot5542', group:4});
                    dataEdges.update({from:'plebbot6197', to:'plebbot5542'});
                }
              }, false);      

            network.on('click', (params) => {
                window.grapher.graphData(params.nodes[0]);
            });

            network.selectNodes([window.networkIds[0]]);
            window.grapher.graphData(network.getSelectedNodes()[0]);               
            document.body.addEventListener("click", function (e) {
                if (e.target.className.split(" ")[0] === "mbtn") {
                    var key = e.target.getAttribute("data-monitor-key");
                    window.grapher.graphData(network.getSelectedNodes()[0], key);
                }
            });            
        });
    });
})();