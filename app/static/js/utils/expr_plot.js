function create_expr(row, maxTpm) {
  /*
        input.forEach(function (t) {
            t['label'] = {
                emphasis: {
                    show: true,
                    formatter: function (param) {
                        return param.data[2];
                    },
                    position: 'top'
                }
            }
        });
  */
        option = {
            tooltip : {
            trigger: 'axis'
    	    },
            toolbox: {
                show: true,
                feature: {
                    mark: {show: true},
                    dataZoom: {show: true},
                    dataView: {show: true, readOnly: false},
                    restore: {show: true},
                    saveAsImage: {show: true}
                }
            },
            xAxis: [
                {   
                    axisLabel: {  
  				interval: 0,  
   				rotate: 25
		    }, 
                    type: 'category',
                    data: ['aleurone_layer', 'anther', 'awns', 'axillary_roots', 'blade', 'coleoptile', 'embryo_proper',
                           'endosperm', 'endosperm_coat', 'leaf_flag', 'glumes', 'grain', 'internode', 'leaf', 'leaf_ligule',
                           'leaf_senescence', 'lemma', 'microspores', 'ovary', 'peduncle', 'pistil', 'rachis', 'radicle', 'roots',
                           'seed_coat', 'seedling', 'sheath', 'shoots', 'spike', 'stamen', 'stem', 'stigma_ovary', 'transfer_cells']
                }
            ],
            yAxis: [
                {
                    type: 'value',
                    scale: true,
                    max: maxTpm,
                    name: "log2(TPM + 1)",                    
                }
            ],
            series: [
              {
                "type": "bar",
                "data": row
              }
            ]
        };
        return option;
    }

function expr_bar(row, maxTpm){
  var expr_plot = echarts.init(document.getElementById('expr-plot'));
  option = create_expr(row, maxTpm);
  expr_plot.setOption(option);
}
