(function() {
    var container = document.getElementById('networkview');
    fetch('/network').then((res) => {
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

            dataNodes = new vis.DataSet(data.nodes)
            dataEdges = new vis.DataSet(data.edges)
            vData = {nodes: dataNodes, edges: dataEdges}


            network = new vis.Network(container, vData, options);
            network.on('click', function(params) {
                console.log(params.nodes[0])
                dataNodes.update({id:100, label:'hello', group:1})
                dataEdges.update({from:1, to:100})
            });
        });
    });
})();