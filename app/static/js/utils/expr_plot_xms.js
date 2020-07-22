function create_expr_xms(tissue, exp, maxTpm) {
    option = {
      color: ["#3398DB"],
      tooltip: {
        trigger: "axis",
      },
      grid: {
        bottom: "25%",
      },
      toolbox: {
        show: true,
        feature: {
          mark: { show: true },
          dataZoom: { show: true },
          dataView: { show: true, readOnly: false },
          restore: { show: true },
          saveAsImage: { show: true },
        },
      },
      xAxis: [
        {
          axisLabel: {
            interval: 0,
            rotate: 45,
          },
          type: "category",
          data: tissue,
        },
      ],
      yAxis: [
        {
          type: "value",
          scale: true,
          max: maxTpm,
          name: "log2(TPM + 1)",
        },
      ],
      series: [
        {
          data: exp,
          type: "bar",          
        },
      ],
    };
    return option;
  }
  
  function expr_bar_xms(tissue, exp, maxTpm) {
    var expr_plot_xms = echarts.init(document.getElementById("expr-plot-2"));
    const option = create_expr_xms(tissue, exp, maxTpm);
    expr_plot_xms.setOption(option);
  }
  