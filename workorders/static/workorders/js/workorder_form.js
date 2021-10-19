//data to send back to databas
var dataStorage = {
  data: [],
  addData: function(obj) {
    this.data.push(obj);
  },
  changeQuantity: function(obj, index) {
    this.data[index].quantity = obj;
  },
  changeProduct: function(obj, index) {
    this.data[index].Product_id = obj;
  },
  changeDimension: function(obj,index) {
    this.data[index].Dimension_id = obj;
  },
  changeStyle: function(obj, index) {
    this.data[index].Style_id = obj;
  }
};

/*
The Category class handles the first Tab within the ProductCart.
It is the container for the tabs to be rendered.
*/
var Category = React.createClass({
  _handleClick: function(tab) {
    this.props._changeTab(tab);
  },
  render: function() {
    return ( 
      <ul className = "nav nav-default nav-stacked col-lg-2" id="tabs"> 
        {this.props.tabList.map(function(tab) {
            return ( 
              <CategoryTab 
                isCurrent = {(this.props.currentTab === tab.id)}
                name = {tab.name}
                key = {tab.id}
                _handleClick = {this._handleClick.bind(this, tab)}
              />
            );
          }.bind(this))
        } 
      </ul>
    );
  }
});

/*
The CategoryTab class is a child of Category class. This class handles the
rendering of each tab.
*/
var CategoryTab = React.createClass({
  _handleClick: function(e) {
    e.preventDefault();
    this.props._handleClick();
  },
  render: function() {
    return (
      <li 
        className = {this.props.isCurrent ? 'active selected' : null}
        role = "presentation"
      > 
        <a 
          onClick = {this._handleClick}
          href = "#"> {this.props.name} 
        </a>
      </li>
    );
  }
});

/*
The Content class is a container for the second column tabs.
This will contain the tabs that will be rendered by Product.
*/
var Content = React.createClass({
  getInitialState: function() {
    return {
      itemList: product_list
    }
  },
  _handleClick: function(id) {
    this.props._changeSecondTab(id);
  },
  render: function() {
    return (
      <div>
        <Product
          secondTab = {this.props.secondTab}
          id = {this.props.currentTab}
          itemList = {this.state.itemList}
          _changeSecondTab = {this._handleClick}
        />
      </div>
    );
  }
});

/*
The Product class handles each tab that is displayed.
*/
var Product = React.createClass({
  _handleClick: function(id){
    this.props._changeSecondTab(id);
  },
  render: function() {
    var previousValue = 0; //temp value
    var products = this.props.itemList.map(function(item, index) {
      if (item.category_id === this.props.id) { //props.id is currentTab
        if (previousValue !== item.id) { //checks to see if duplicate product
          previousValue = item.id; //assign non-duplicate value
          return ( 
            <li
              className = {(this.props.secondTab === item.id) ? 'active selected' : null}
              role = "presentation"
              key={index}>

              <a onClick={this._handleClick.bind(this, item.id)} href="#" > 
                {item.name}
              </a>
            </li>
          );
        }
      }
    }.bind(this));
    return (
        <ul className = "nav nav-default nav-stacked col-lg-2">{products} </ul>
      );
  }
});

/*
The Dimension class is the last column of the ProductMenu. This class is a container
for the DimensionStyle. 
*/
var Dimension = React.createClass({
  render: function() {
      var result = [];
      var tempValue;
      this.props.itemList.map(function(item, index) {
        if(this.props.currentSecondTab === item.id) { //grab current tab
          if(item.dimensions__name) { //check to see if any Dimension
            if(tempValue !== item.dimensions__name) {
              tempValue = item.dimensions__name;
              result.push(
                <div className="col-lg-4 text-center">
                  <DimensionStyle 
                    item = {item}
                    itemList = {this.props.itemList}
                    _changeData = {this.props._changeData}
                   /> 
                </div>
              );
            }
          }
        }
      }.bind(this));
      return (
      <div className="col-lg-8 row">
        {result}
      </div>
      );
  }
});

/*
The DimensionStyle class will display different types of choices for the user.
This class handles with the dataStorage manipulation, preparing it to send to the 
Database. The class handles the function of adding user's selection to the dataStorage.
*/
var DimensionStyle = React.createClass({
  getInitialState: function() {
    return {
      quantity: 1,
      style: 0
    }
  },
  _handlePlusButton: function(e) {
    var obj = {
      Product_id: this.props.item.id,
      Dimension_id: this.props.item.dimensions__id,
      Style_id: parseInt(this.state.style),
      quantity: this.state.quantity,
    };
    this.props._changeData(obj);
    $("#tester").val(null).change();
    this.setState({quantity: 1, style: 0});
  },
  _handleChange: function(event) {
    this.setState({quantity: event.target.value})
  },
  _setStyle: function(event) {
    this.setState({style: event.target.value});
  },
  render: function() {
    var styleList = [];

    function findStyle(item) { //function to check if item is in array
      for(var x in styleList) {
        if(styleList[x].name === item) {
          return true;
        }
      }
      return false;
    };

    for(var x in this.props.itemList) { //for loop through itemList
      if(this.props.itemList[x].id === this.props.item.id) { //finds only object of related item
        if(findStyle(this.props.itemList[x].dimensions__styles__name)) { //checks to see if style already in array
          //do nothing
        } else {
          styleList.push({
            id: this.props.itemList[x].dimensions__styles__id,
            name: this.props.itemList[x].dimensions__styles__name}
          ); //add style into array
          if(x === 0) {
            this.setState({style: this.props.itemList[x].dimensions__styles__id});
          }
        }
      }
    };

    return (
      <div className="styleBox">
        <div id="attribute">{this.props.item.dimensions__name} </div>
        <select className="form-control" onChange={this._setStyle} id="tester"> 
        <option value={null}> </option>
        {styleList.map(function(style) {
            if(style.name !== null) {
              return ( 
                <option value={style.id}> {style.name} </option>
              );
            }
          }.bind(this))
        }
        </select>
        <div className="input-group">
              <span className="input-group-addon">
              <span>Qty:</span>
              </span>
              <input type="number" className="form-control" min="1" placeholder="1" value={this.state.quantity} onChange={this._handleChange}/>
        </div>
        <button type="button" className="form-control" onClick={this._handlePlusButton}> <span className="glyphicon glyphicon-plus"></span></button> 
      </div>
    );
  }
});

/*
The Product Menu contains all the tabs and views for adding a product/service to user's cart.
The class has an ItemList, tabList, currentTab, and secondTab state. These states are implemented
so react can see any change of data for re-rendering.
*/
var ProductMenu = React.createClass({
    getInitialState: function() {
      return {
        itemList: product_list,
        tabList: category_list, 
        currentTab: 1,
        secondTab: 0,
      };
    },
    _changeTab: function(tab) {
      this.setState({
        currentTab: tab.id,
        secondTab: 0
      });
    },
    _changeSecondTab: function(id) {
      this.setState({
        secondTab: id
      });
    },
    render: function() {
      return (
      <div className="col-lg-8">
        <div className="panel panel-default">
          <div className="panel-heading">
            Products
          </div>
          <div className="panel-body row">
            <Category 
              currentTab = {this.state.currentTab}
              _changeTab = {this._changeTab}
              tabList = {this.state.tabList}
            /> 
            <Content 
              currentTab = {this.state.currentTab}
              secondTab = {this.state.secondTab}
              _changeSecondTab = {this._changeSecondTab}
            />
            <Dimension 
            currentSecondTab = {this.state.secondTab}
            itemList = {this.state.itemList}
            _changeData = {this.props._changeData}
            />
          </div>
        </div>
      </div>
      
    );
  }
});

/*
The ProductCart class handles the view of showing what the user added to their list.

*/
var ProductCart = React.createClass({
  render: function(){
    var handleRemover = function(dataObject, changeData) {
      var data;
      for(var x in dataStorage.data) {
        if(dataStorage.data[x] === dataObject) {
          dataStorage.data.splice(x,1);
        }
      }
      this.props._setData(dataStorage);
    }.bind(this);
    var results = [];
    if(this.props.dataStorage.data.length !== 0) {
      this.props.dataStorage.data.map(function(dataObject, index){
        var product, dimension, style;
        for(var x in product_list) {
          if(product_list[x].id === dataObject.Product_id) { //finding product
            product = product_list[x].name;
          }
          if(product_list[x].dimensions__id === dataObject.Dimension_id) { //finding dimension
            dimension = product_list[x].dimensions__name;
          }
          if(product_list[x].dimensions__styles__id === dataObject.Style_id) { //finding style
            style = product_list[x].dimensions__styles__name;
          }
        }
        results.push(
          <div key={index}>
            <span className="col-lg-1 glyphicon glyphicon-remove" onClick={handleRemover.bind(this, dataObject)}></span>
            <div className="col-lg-2"> {product} </div>
            <div className="col-lg-3"> {dimension} </div>
            <div className="col-lg-4"> {style} </div>
            <div className="col-lg-2"> {dataObject.quantity} </div>
          </div>
        );
      });
    }
    
    return(
      <div className="col-lg-4">
        <div className="panel panel-default">
          <div className="panel-heading">
            Products Cart
          </div>
          <div className="panel-body">
              {(results.length < 1) ? 'Your cart is empty.' : results}
          </div>
        </div>
      </div>

    );
  }
});

//The Packages class is the parent class of the package functionality.
/* -----------WORK IN PROGRESS----------- */
var Packages = React.createClass({
  render: function() {
    return (
      <div className="col-lg-12 package">
        <PackageItems />
      </div>
    );
  }
});

//The PackageItems class is a child class that will handle each packages
/* -----------WORK IN PROGRESS----------- */
var PackageItems = React.createClass({
  render: function() {
    return (
      <div className="package item">
        item
      </div>
    );
  }
})

/*
custom function that checks objects.
*/
function filterData(obj1, obj2) {
  if(obj1.Product_id !== obj2.Product_id) {
    return false;
  } else {
    if(obj1.Dimension_id !== obj2.Dimension_id) {
      return false;
    } else {
      if(obj1.Style_id !== obj2.Style_id) {
        return false;
      } else {
        return true;
      }
    }
  }
}
/*
The main parent class of the react component
Renders two child components of ProductMenu and ProductCart
Container passes a function param into ProductMenu and the state in ProductCart
Holds a state of the structured data that is packed in ProductMenu
Data is then displayed in ProductCart
*/
var Container = React.createClass({
  getInitialState: function() { //initializing state
    return {
      dataStorage
    }
  },
  _setData : function(data) {
    this.setState({dataStorage: data});
  },
  _changeData : function(data){ //function that updates state
    var present;
    for(var x in this.state.dataStorage.data) {
      present = filterData(data, this.state.dataStorage.data[x]);
      if(present) {
        if(data.quantity !== this.state.dataStorage.data[x].quantity) {
          dataStorage.changeQuantity(data.quantity, x);
          break;
        } else {
          return; //data is all the same inside. do nothing
        }
        break;
      }
    }
    if(!present) {    
      dataStorage.addData(data);
    }

    this.setState({
      dataStorage: dataStorage
    });
  },
  render: function () {
    return (
      <div className="form-group">
        <ProductMenu _changeData = {this._changeData}/>
        <div className="row">
          <ProductCart dataStorage = {this.state.dataStorage} _setData={this._setData}/>
        </div>
      </div>
    );
  }
});

//ReactDom points to the html to locate where the react component class, Container, will be rendered
//Container takes in the variable dataStorage
ReactDOM.render( <Container dataStorage={dataStorage}/> , document.getElementById('appContainer'));

console.log(category_list);
console.log(product_list);