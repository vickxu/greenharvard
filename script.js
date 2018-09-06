/**
 * Green Harvard - script.js 
 * Vicky Xu and Rebecca Hao - z_xu@college.harvard.edu, rhao@college.harvard.edu
 * CS50 Fall 2016
 * Based off code from: http://findnerd.com/list/view/How-to-create-dynamic-checkbox-using-JavaScript/5746/
 */ 

var points = 0;

// create new task information function
function createchkboxes(elem) {
    var label = document.createElement('label');
    var br = document.createElement('br');
    var alabel = document.getElementById('div1');
    var last = alabel[alabel.length - 1];
    label.htmlFor = "lbl";
    
    // create checkbox for task
    label.appendChild(Createcheckbox(elem));
    label.appendChild(document.createTextNode(elem.value));

    // POST call to send task id information to application
    $.post( "/postmethod", {
        javascript_data2: elem.id
    });
    
    document.getElementById('div1').appendChild(label);
    document.getElementById('div1').appendChild(br);
    
    // disable buttons if task already chosen
    if (points == 0)
    {
        ReableNextButton(elem.id);
    }
    DisableNextButton(elem.id);
}

// remove task checkbox
function removeBox(btn) {
    var label = btn.parentNode;
    label.removeChild(btn);
    label.parentNode.removeChild(label);
}

// create the task checkbox
function Createcheckbox(elem) {
    var checkbox = document.createElement('input');
    checkbox.type = "checkbox";
    checkbox.onclick = function(){
        points++;
        this.onclick = null;
        removeBox(this);
        
        // POST call to send back task id to remove
        $.post( "/remove", {
        removeid: elem.id
        });
    }
    return checkbox;
}
       
function getValues(divId){
  alert(points);
}

// disable button
function DisableNextButton(btnId) {
    document.getElementById(btnId).disabled = 'true';
}

// re-enable button
function ReableNextButton(btnId) {
    document.getElementById(btnId).disabled = 'true';
}