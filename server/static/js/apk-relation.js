var dom = document.getElementById('chart-container');
document.oncontextmenu = function() {
  return false
}
var nodes = "";
var myChart = echarts.init(dom, null, {
  renderer: 'svg',
  useDirtyRect: true,
});

myChart.on('contextmenu', showMenu);
function showMenu(param){
  var menu = document.getElementById("struct_menu");
  var event = param.event;
  menu.style.left = event.offsetX + 'px';
  menu.style.top = event.offsetY + 20 + 'px';
  menu.style.display = "block";
}

var app = {};
var option;
date = getUrlParamValue(location.href,'date')
project = getUrlParamValue(location.href,'project')
type = getUrlParamValue(location.href,'type')
filter = getUrlParamValue(location.href,'filter')

myChart.showLoading();

function getUrlParamValue(url, name) {
  var value = '';
  url.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(str, key, val) {
      if (key === name) {
          value = decodeURIComponent(val);
      }
  });
  return value;
}

function loadData(date,project,type){
  $.getJSON("/get/relations?date=" + date + "&project=" + project + "&type=" + type + "&filter=" + filter, function (graph) {
    nodes = graph.nodes;
    myChart.hideLoading();
    graph.nodes.forEach(function (node) {
      node.label = {
        show:true
      };
    });
    option = {
      tooltip: {

      },
      toolbox: {
        show : true, 
        orient:"vertical",
        itemSize:15,
        itemGap:10, 
        showTitle:true, 
        zlevel:0, 
        z:2,
        left:"left", 
        top:"top",
        right:"auto", 
        bottom:"auto",
        width:"auto", 
        height:"auto",
        feature : {
            mark : {                                
                show: true
            },
            dataView : {                            
                show: true, 
                title:"Date View",
                readOnly: false,
                lang: ['Date View', 'Close', 'Update'], 
                backgroundColor:"#fff", 
                textareaColor:"#fff", 
                textareaBorderColor:"#333", 
                textColor:"#000", 
                buttonColor:"#c23531",
                buttonTextColor:"#fff", 
            },

            mySwitchPart: {
              show: true,
              title: 'Part',
              icon: 'path://M221.8,0v256l-181,181c46.4,46.3,110.4,75,181,75c141.4,0,256-114.6,256-256S363.2,0,221.8,0z',
              onclick: function (){
                myChart.clear();
                loadData(date,project,'part');
              }
            },
            mySwitchAll: {
              show: true,
              title: 'All',
              icon: 'path://M24 40c-8.822 0-16-7.178-16-16S15.178 8 24 8s16 7.178 16 16-7.178 16-16 16z',
              onclick: function (){
                myChart.clear();
                loadData(date,project,'all');
              }
            },
            saveAsImage : {                        
              show: true, 
              type:"png", 
              name:"apk_relation",
              backgroundColor:"#ffffff",
              title:"Export",
              pixelRatio:1 
            },
            myProject: {
              show: true,
              title: 'Github',
              icon: 'path://M23.546 10.93 13.067.452a1.55 1.55 0 0 0-2.188 0L8.708 2.627l2.76 2.76a1.838 1.838 0 0 1 2.327 2.341l2.658 2.66a1.838 1.838 0 0 1 1.9 3.039 1.837 1.837 0 0 1-2.6 0 1.846 1.846 0 0 1-.404-1.996L12.86 8.955v6.525c.176.086.342.203.488.348a1.848 1.848 0 0 1 0 2.6 1.844 1.844 0 0 1-2.609 0 1.834 1.834 0 0 1 0-2.598c.182-.18.387-.316.605-.406V8.835a1.834 1.834 0 0 1-.996-2.41L7.636 3.7.45 10.881c-.6.605-.6 1.584 0 2.189l10.48 10.477a1.545 1.545 0 0 0 2.186 0l10.43-10.43a1.544 1.544 0 0 0 0-2.187',
              onclick: function (){
                window.open('https://github.com/delikely/ERH','_blank')
              }
            },
            myAbout: {
              show: true,
              title: 'About',
              // icon: 'image:// ',
              icon: 'path://M4.479,13.325 L5.852,4.703 C5.852,4.703 5.881,4.004 5.216,4.004 C3.715,4.004 -0.074,4.008 -0.074,4.008 C-0.074,4.008 3.905,4.721 3.905,6.067 C3.905,6.067 2.597,11.827 2.597,13.357 C2.597,14.888 3.433,16.001 4.934,16.001 C6.159,16.001 7.272,14.665 7.188,12.718 C5.991,14.554 4.479,14.82 4.479,13.325 L4.479,13.325 Z',
              onclick: function (){
                  alert('Powered By 饭饭')
              }
            },
        },
    },

      legend: [
        {
          // selectedMode: 'single',
          data: graph.categories.map(function (a) {
            return a.name;
          })
        }
      ],
      animationDuration: 1500,
      animationEasingUpdate: 'quinticInOut',
      series: [
        {
          name: 'APK relation',
          type: 'graph',
          layout: 'force',
          data: graph.nodes,
          links: graph.links,
          edgeSymbol: ['', 'arrow'],
          roam: true,
          symbolSize: 10, 
          label: {
            show: true,
            position: 'right',
            formatter: '{b}'
          },
          lineStyle: {
            color: 'source',
            curveness: 0.3,
            width: 2
          },
          emphasis: {
            focus: 'adjacency',
            lineStyle: {
              width: 10
            },
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    };
    myChart.setOption(option);
  });

}

loadData(date,project,type);

if (option && typeof option === 'object') {
  myChart.setOption(option);
}

window.addEventListener('resize', myChart.resize);
window.scrollBy(0, 100);

myChart.on('dblclick', function(params) {
  var file = params.name;
  var request = "/apk-relation?date=" + date + "&project=" + project + "&type=all&filter=" + file;
  window.open(request);
});