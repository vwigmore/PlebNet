(function() {
    window.grapher = window.grapher || {};
    var grapher = window.grapher;

    grapher.lastGraph = undefined;
    grapher.units = {
        'MB_balance' : 'MBs',
        'downloaded' : 'MBs',
        'uploaded' : 'MBs',
        'matchmakers' : 'peers'
    };
    grapher.defaultSelection = 'uploaded';
    grapher.selected = grapher.defaultSelection;

    grapher.graphData = function(node, key) {
        if (typeof key === 'undefined') {
            key = grapher.selected;
        } else {
            grapher.selected = key;
        }

        fetch('/node/'+node+'/'+key).then((nodeRes) => {
            nodeRes.json().then((nodeData) => {
                window.grapher.graph(key, nodeData)
            });
        });        
    };

    grapher.graph = function(key, data) {
        var graph_container = document.getElementById('plebgraphs');
        var dataset = new vis.DataSet(data);
        var options = {
            start: data[0].x,
            end: data[data.length-1].x,         
            dataAxis: {
                showMinorLabels: false,
                left: {
                    title: {
                        text: key + ' (' + grapher.units[key] + ')'
                    },
                    range: {
                        min: 0,
                        max: data[data.length-1].y * 1.5 
                    }
                }
            },
            drawPoints: true,
            shaded: {
                orientation: 'zero' // top, bottom
            },        
            autoResize: true,
            moveable: false,
            graphHeight: '395px',
        }

        if (grapher.lastGraph) {
            grapher.lastGraph.destroy();
        }


        var groups = new vis.DataSet();
        groups.add({
            id: 0,
            content: 'namess',
            className: 'custom-style1',
            options: {
                drawPoints: {
                    style: 'square' // square, circle
                },
                shaded: {
                    orientation: 'bottom' // top, bottom
                }
            }});        

        grapher.lastGraph = new vis.Graph2d(graph_container, dataset, groups, options);          
    }
}) ();
