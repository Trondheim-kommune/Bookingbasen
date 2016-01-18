/*! jQuery UI - v1.10.3 - 2013-05-22
* http://jqueryui.com
* Includes: jquery.ui.core.js, jquery.ui.widget.js, jquery.ui.mouse.js, jquery.ui.draggable.js, jquery.ui.droppable.js, jquery.ui.resizable.js
* Copyright 2013 jQuery Foundation and other contributors Licensed MIT */

(function(e,t){function i(t,i){var a,n,r,o=t.nodeName.toLowerCase();return"area"===o?(a=t.parentNode,n=a.name,t.href&&n&&"map"===a.nodeName.toLowerCase()?(r=e("img[usemap=#"+n+"]")[0],!!r&&s(r)):!1):(/input|select|textarea|button|object/.test(o)?!t.disabled:"a"===o?t.href||i:i)&&s(t)}function s(t){return e.expr.filters.visible(t)&&!e(t).parents().addBack().filter(function(){return"hidden"===e.css(this,"visibility")}).length}var a=0,n=/^ui-id-\d+$/;e.ui=e.ui||{},e.extend(e.ui,{version:"1.10.3",keyCode:{BACKSPACE:8,COMMA:188,DELETE:46,DOWN:40,END:35,ENTER:13,ESCAPE:27,HOME:36,LEFT:37,NUMPAD_ADD:107,NUMPAD_DECIMAL:110,NUMPAD_DIVIDE:111,NUMPAD_ENTER:108,NUMPAD_MULTIPLY:106,NUMPAD_SUBTRACT:109,PAGE_DOWN:34,PAGE_UP:33,PERIOD:190,RIGHT:39,SPACE:32,TAB:9,UP:38}}),e.fn.extend({focus:function(t){return function(i,s){return"number"==typeof i?this.each(function(){var t=this;setTimeout(function(){e(t).focus(),s&&s.call(t)},i)}):t.apply(this,arguments)}}(e.fn.focus),scrollParent:function(){var t;return t=e.ui.ie&&/(static|relative)/.test(this.css("position"))||/absolute/.test(this.css("position"))?this.parents().filter(function(){return/(relative|absolute|fixed)/.test(e.css(this,"position"))&&/(auto|scroll)/.test(e.css(this,"overflow")+e.css(this,"overflow-y")+e.css(this,"overflow-x"))}).eq(0):this.parents().filter(function(){return/(auto|scroll)/.test(e.css(this,"overflow")+e.css(this,"overflow-y")+e.css(this,"overflow-x"))}).eq(0),/fixed/.test(this.css("position"))||!t.length?e(document):t},zIndex:function(i){if(i!==t)return this.css("zIndex",i);if(this.length)for(var s,a,n=e(this[0]);n.length&&n[0]!==document;){if(s=n.css("position"),("absolute"===s||"relative"===s||"fixed"===s)&&(a=parseInt(n.css("zIndex"),10),!isNaN(a)&&0!==a))return a;n=n.parent()}return 0},uniqueId:function(){return this.each(function(){this.id||(this.id="ui-id-"+ ++a)})},removeUniqueId:function(){return this.each(function(){n.test(this.id)&&e(this).removeAttr("id")})}}),e.extend(e.expr[":"],{data:e.expr.createPseudo?e.expr.createPseudo(function(t){return function(i){return!!e.data(i,t)}}):function(t,i,s){return!!e.data(t,s[3])},focusable:function(t){return i(t,!isNaN(e.attr(t,"tabindex")))},tabbable:function(t){var s=e.attr(t,"tabindex"),a=isNaN(s);return(a||s>=0)&&i(t,!a)}}),e("<a>").outerWidth(1).jquery||e.each(["Width","Height"],function(i,s){function a(t,i,s,a){return e.each(n,function(){i-=parseFloat(e.css(t,"padding"+this))||0,s&&(i-=parseFloat(e.css(t,"border"+this+"Width"))||0),a&&(i-=parseFloat(e.css(t,"margin"+this))||0)}),i}var n="Width"===s?["Left","Right"]:["Top","Bottom"],r=s.toLowerCase(),o={innerWidth:e.fn.innerWidth,innerHeight:e.fn.innerHeight,outerWidth:e.fn.outerWidth,outerHeight:e.fn.outerHeight};e.fn["inner"+s]=function(i){return i===t?o["inner"+s].call(this):this.each(function(){e(this).css(r,a(this,i)+"px")})},e.fn["outer"+s]=function(t,i){return"number"!=typeof t?o["outer"+s].call(this,t):this.each(function(){e(this).css(r,a(this,t,!0,i)+"px")})}}),e.fn.addBack||(e.fn.addBack=function(e){return this.add(null==e?this.prevObject:this.prevObject.filter(e))}),e("<a>").data("a-b","a").removeData("a-b").data("a-b")&&(e.fn.removeData=function(t){return function(i){return arguments.length?t.call(this,e.camelCase(i)):t.call(this)}}(e.fn.removeData)),e.ui.ie=!!/msie [\w.]+/.exec(navigator.userAgent.toLowerCase()),e.support.selectstart="onselectstart"in document.createElement("div"),e.fn.extend({disableSelection:function(){return this.bind((e.support.selectstart?"selectstart":"mousedown")+".ui-disableSelection",function(e){e.preventDefault()})},enableSelection:function(){return this.unbind(".ui-disableSelection")}}),e.extend(e.ui,{plugin:{add:function(t,i,s){var a,n=e.ui[t].prototype;for(a in s)n.plugins[a]=n.plugins[a]||[],n.plugins[a].push([i,s[a]])},call:function(e,t,i){var s,a=e.plugins[t];if(a&&e.element[0].parentNode&&11!==e.element[0].parentNode.nodeType)for(s=0;a.length>s;s++)e.options[a[s][0]]&&a[s][1].apply(e.element,i)}},hasScroll:function(t,i){if("hidden"===e(t).css("overflow"))return!1;var s=i&&"left"===i?"scrollLeft":"scrollTop",a=!1;return t[s]>0?!0:(t[s]=1,a=t[s]>0,t[s]=0,a)}})})(jQuery);(function(e,t){var i=0,s=Array.prototype.slice,n=e.cleanData;e.cleanData=function(t){for(var i,s=0;null!=(i=t[s]);s++)try{e(i).triggerHandler("remove")}catch(a){}n(t)},e.widget=function(i,s,n){var a,r,o,h,l={},u=i.split(".")[0];i=i.split(".")[1],a=u+"-"+i,n||(n=s,s=e.Widget),e.expr[":"][a.toLowerCase()]=function(t){return!!e.data(t,a)},e[u]=e[u]||{},r=e[u][i],o=e[u][i]=function(e,i){return this._createWidget?(arguments.length&&this._createWidget(e,i),t):new o(e,i)},e.extend(o,r,{version:n.version,_proto:e.extend({},n),_childConstructors:[]}),h=new s,h.options=e.widget.extend({},h.options),e.each(n,function(i,n){return e.isFunction(n)?(l[i]=function(){var e=function(){return s.prototype[i].apply(this,arguments)},t=function(e){return s.prototype[i].apply(this,e)};return function(){var i,s=this._super,a=this._superApply;return this._super=e,this._superApply=t,i=n.apply(this,arguments),this._super=s,this._superApply=a,i}}(),t):(l[i]=n,t)}),o.prototype=e.widget.extend(h,{widgetEventPrefix:r?h.widgetEventPrefix:i},l,{constructor:o,namespace:u,widgetName:i,widgetFullName:a}),r?(e.each(r._childConstructors,function(t,i){var s=i.prototype;e.widget(s.namespace+"."+s.widgetName,o,i._proto)}),delete r._childConstructors):s._childConstructors.push(o),e.widget.bridge(i,o)},e.widget.extend=function(i){for(var n,a,r=s.call(arguments,1),o=0,h=r.length;h>o;o++)for(n in r[o])a=r[o][n],r[o].hasOwnProperty(n)&&a!==t&&(i[n]=e.isPlainObject(a)?e.isPlainObject(i[n])?e.widget.extend({},i[n],a):e.widget.extend({},a):a);return i},e.widget.bridge=function(i,n){var a=n.prototype.widgetFullName||i;e.fn[i]=function(r){var o="string"==typeof r,h=s.call(arguments,1),l=this;return r=!o&&h.length?e.widget.extend.apply(null,[r].concat(h)):r,o?this.each(function(){var s,n=e.data(this,a);return n?e.isFunction(n[r])&&"_"!==r.charAt(0)?(s=n[r].apply(n,h),s!==n&&s!==t?(l=s&&s.jquery?l.pushStack(s.get()):s,!1):t):e.error("no such method '"+r+"' for "+i+" widget instance"):e.error("cannot call methods on "+i+" prior to initialization; "+"attempted to call method '"+r+"'")}):this.each(function(){var t=e.data(this,a);t?t.option(r||{})._init():e.data(this,a,new n(r,this))}),l}},e.Widget=function(){},e.Widget._childConstructors=[],e.Widget.prototype={widgetName:"widget",widgetEventPrefix:"",defaultElement:"<div>",options:{disabled:!1,create:null},_createWidget:function(t,s){s=e(s||this.defaultElement||this)[0],this.element=e(s),this.uuid=i++,this.eventNamespace="."+this.widgetName+this.uuid,this.options=e.widget.extend({},this.options,this._getCreateOptions(),t),this.bindings=e(),this.hoverable=e(),this.focusable=e(),s!==this&&(e.data(s,this.widgetFullName,this),this._on(!0,this.element,{remove:function(e){e.target===s&&this.destroy()}}),this.document=e(s.style?s.ownerDocument:s.document||s),this.window=e(this.document[0].defaultView||this.document[0].parentWindow)),this._create(),this._trigger("create",null,this._getCreateEventData()),this._init()},_getCreateOptions:e.noop,_getCreateEventData:e.noop,_create:e.noop,_init:e.noop,destroy:function(){this._destroy(),this.element.unbind(this.eventNamespace).removeData(this.widgetName).removeData(this.widgetFullName).removeData(e.camelCase(this.widgetFullName)),this.widget().unbind(this.eventNamespace).removeAttr("aria-disabled").removeClass(this.widgetFullName+"-disabled "+"ui-state-disabled"),this.bindings.unbind(this.eventNamespace),this.hoverable.removeClass("ui-state-hover"),this.focusable.removeClass("ui-state-focus")},_destroy:e.noop,widget:function(){return this.element},option:function(i,s){var n,a,r,o=i;if(0===arguments.length)return e.widget.extend({},this.options);if("string"==typeof i)if(o={},n=i.split("."),i=n.shift(),n.length){for(a=o[i]=e.widget.extend({},this.options[i]),r=0;n.length-1>r;r++)a[n[r]]=a[n[r]]||{},a=a[n[r]];if(i=n.pop(),s===t)return a[i]===t?null:a[i];a[i]=s}else{if(s===t)return this.options[i]===t?null:this.options[i];o[i]=s}return this._setOptions(o),this},_setOptions:function(e){var t;for(t in e)this._setOption(t,e[t]);return this},_setOption:function(e,t){return this.options[e]=t,"disabled"===e&&(this.widget().toggleClass(this.widgetFullName+"-disabled ui-state-disabled",!!t).attr("aria-disabled",t),this.hoverable.removeClass("ui-state-hover"),this.focusable.removeClass("ui-state-focus")),this},enable:function(){return this._setOption("disabled",!1)},disable:function(){return this._setOption("disabled",!0)},_on:function(i,s,n){var a,r=this;"boolean"!=typeof i&&(n=s,s=i,i=!1),n?(s=a=e(s),this.bindings=this.bindings.add(s)):(n=s,s=this.element,a=this.widget()),e.each(n,function(n,o){function h(){return i||r.options.disabled!==!0&&!e(this).hasClass("ui-state-disabled")?("string"==typeof o?r[o]:o).apply(r,arguments):t}"string"!=typeof o&&(h.guid=o.guid=o.guid||h.guid||e.guid++);var l=n.match(/^(\w+)\s*(.*)$/),u=l[1]+r.eventNamespace,c=l[2];c?a.delegate(c,u,h):s.bind(u,h)})},_off:function(e,t){t=(t||"").split(" ").join(this.eventNamespace+" ")+this.eventNamespace,e.unbind(t).undelegate(t)},_delay:function(e,t){function i(){return("string"==typeof e?s[e]:e).apply(s,arguments)}var s=this;return setTimeout(i,t||0)},_hoverable:function(t){this.hoverable=this.hoverable.add(t),this._on(t,{mouseenter:function(t){e(t.currentTarget).addClass("ui-state-hover")},mouseleave:function(t){e(t.currentTarget).removeClass("ui-state-hover")}})},_focusable:function(t){this.focusable=this.focusable.add(t),this._on(t,{focusin:function(t){e(t.currentTarget).addClass("ui-state-focus")},focusout:function(t){e(t.currentTarget).removeClass("ui-state-focus")}})},_trigger:function(t,i,s){var n,a,r=this.options[t];if(s=s||{},i=e.Event(i),i.type=(t===this.widgetEventPrefix?t:this.widgetEventPrefix+t).toLowerCase(),i.target=this.element[0],a=i.originalEvent)for(n in a)n in i||(i[n]=a[n]);return this.element.trigger(i,s),!(e.isFunction(r)&&r.apply(this.element[0],[i].concat(s))===!1||i.isDefaultPrevented())}},e.each({show:"fadeIn",hide:"fadeOut"},function(t,i){e.Widget.prototype["_"+t]=function(s,n,a){"string"==typeof n&&(n={effect:n});var r,o=n?n===!0||"number"==typeof n?i:n.effect||i:t;n=n||{},"number"==typeof n&&(n={duration:n}),r=!e.isEmptyObject(n),n.complete=a,n.delay&&s.delay(n.delay),r&&e.effects&&e.effects.effect[o]?s[t](n):o!==t&&s[o]?s[o](n.duration,n.easing,a):s.queue(function(i){e(this)[t](),a&&a.call(s[0]),i()})}})})(jQuery);(function(e){var t=!1;e(document).mouseup(function(){t=!1}),e.widget("ui.mouse",{version:"1.10.3",options:{cancel:"input,textarea,button,select,option",distance:1,delay:0},_mouseInit:function(){var t=this;this.element.bind("mousedown."+this.widgetName,function(e){return t._mouseDown(e)}).bind("click."+this.widgetName,function(i){return!0===e.data(i.target,t.widgetName+".preventClickEvent")?(e.removeData(i.target,t.widgetName+".preventClickEvent"),i.stopImmediatePropagation(),!1):undefined}),this.started=!1},_mouseDestroy:function(){this.element.unbind("."+this.widgetName),this._mouseMoveDelegate&&e(document).unbind("mousemove."+this.widgetName,this._mouseMoveDelegate).unbind("mouseup."+this.widgetName,this._mouseUpDelegate)},_mouseDown:function(i){if(!t){this._mouseStarted&&this._mouseUp(i),this._mouseDownEvent=i;var s=this,n=1===i.which,a="string"==typeof this.options.cancel&&i.target.nodeName?e(i.target).closest(this.options.cancel).length:!1;return n&&!a&&this._mouseCapture(i)?(this.mouseDelayMet=!this.options.delay,this.mouseDelayMet||(this._mouseDelayTimer=setTimeout(function(){s.mouseDelayMet=!0},this.options.delay)),this._mouseDistanceMet(i)&&this._mouseDelayMet(i)&&(this._mouseStarted=this._mouseStart(i)!==!1,!this._mouseStarted)?(i.preventDefault(),!0):(!0===e.data(i.target,this.widgetName+".preventClickEvent")&&e.removeData(i.target,this.widgetName+".preventClickEvent"),this._mouseMoveDelegate=function(e){return s._mouseMove(e)},this._mouseUpDelegate=function(e){return s._mouseUp(e)},e(document).bind("mousemove."+this.widgetName,this._mouseMoveDelegate).bind("mouseup."+this.widgetName,this._mouseUpDelegate),i.preventDefault(),t=!0,!0)):!0}},_mouseMove:function(t){return e.ui.ie&&(!document.documentMode||9>document.documentMode)&&!t.button?this._mouseUp(t):this._mouseStarted?(this._mouseDrag(t),t.preventDefault()):(this._mouseDistanceMet(t)&&this._mouseDelayMet(t)&&(this._mouseStarted=this._mouseStart(this._mouseDownEvent,t)!==!1,this._mouseStarted?this._mouseDrag(t):this._mouseUp(t)),!this._mouseStarted)},_mouseUp:function(t){return e(document).unbind("mousemove."+this.widgetName,this._mouseMoveDelegate).unbind("mouseup."+this.widgetName,this._mouseUpDelegate),this._mouseStarted&&(this._mouseStarted=!1,t.target===this._mouseDownEvent.target&&e.data(t.target,this.widgetName+".preventClickEvent",!0),this._mouseStop(t)),!1},_mouseDistanceMet:function(e){return Math.max(Math.abs(this._mouseDownEvent.pageX-e.pageX),Math.abs(this._mouseDownEvent.pageY-e.pageY))>=this.options.distance},_mouseDelayMet:function(){return this.mouseDelayMet},_mouseStart:function(){},_mouseDrag:function(){},_mouseStop:function(){},_mouseCapture:function(){return!0}})})(jQuery);(function(e){e.widget("ui.draggable",e.ui.mouse,{version:"1.10.3",widgetEventPrefix:"drag",options:{addClasses:!0,appendTo:"parent",axis:!1,connectToSortable:!1,containment:!1,cursor:"auto",cursorAt:!1,grid:!1,handle:!1,helper:"original",iframeFix:!1,opacity:!1,refreshPositions:!1,revert:!1,revertDuration:500,scope:"default",scroll:!0,scrollSensitivity:20,scrollSpeed:20,snap:!1,snapMode:"both",snapTolerance:20,stack:!1,zIndex:!1,drag:null,start:null,stop:null},_create:function(){"original"!==this.options.helper||/^(?:r|a|f)/.test(this.element.css("position"))||(this.element[0].style.position="relative"),this.options.addClasses&&this.element.addClass("ui-draggable"),this.options.disabled&&this.element.addClass("ui-draggable-disabled"),this._mouseInit()},_destroy:function(){this.element.removeClass("ui-draggable ui-draggable-dragging ui-draggable-disabled"),this._mouseDestroy()},_mouseCapture:function(t){var i=this.options;return this.helper||i.disabled||e(t.target).closest(".ui-resizable-handle").length>0?!1:(this.handle=this._getHandle(t),this.handle?(e(i.iframeFix===!0?"iframe":i.iframeFix).each(function(){e("<div class='ui-draggable-iframeFix' style='background: #fff;'></div>").css({width:this.offsetWidth+"px",height:this.offsetHeight+"px",position:"absolute",opacity:"0.001",zIndex:1e3}).css(e(this).offset()).appendTo("body")}),!0):!1)},_mouseStart:function(t){var i=this.options;return this.helper=this._createHelper(t),this.helper.addClass("ui-draggable-dragging"),this._cacheHelperProportions(),e.ui.ddmanager&&(e.ui.ddmanager.current=this),this._cacheMargins(),this.cssPosition=this.helper.css("position"),this.scrollParent=this.helper.scrollParent(),this.offsetParent=this.helper.offsetParent(),this.offsetParentCssPosition=this.offsetParent.css("position"),this.offset=this.positionAbs=this.element.offset(),this.offset={top:this.offset.top-this.margins.top,left:this.offset.left-this.margins.left},this.offset.scroll=!1,e.extend(this.offset,{click:{left:t.pageX-this.offset.left,top:t.pageY-this.offset.top},parent:this._getParentOffset(),relative:this._getRelativeOffset()}),this.originalPosition=this.position=this._generatePosition(t),this.originalPageX=t.pageX,this.originalPageY=t.pageY,i.cursorAt&&this._adjustOffsetFromHelper(i.cursorAt),this._setContainment(),this._trigger("start",t)===!1?(this._clear(),!1):(this._cacheHelperProportions(),e.ui.ddmanager&&!i.dropBehaviour&&e.ui.ddmanager.prepareOffsets(this,t),this._mouseDrag(t,!0),e.ui.ddmanager&&e.ui.ddmanager.dragStart(this,t),!0)},_mouseDrag:function(t,i){if("fixed"===this.offsetParentCssPosition&&(this.offset.parent=this._getParentOffset()),this.position=this._generatePosition(t),this.positionAbs=this._convertPositionTo("absolute"),!i){var s=this._uiHash();if(this._trigger("drag",t,s)===!1)return this._mouseUp({}),!1;this.position=s.position}return this.options.axis&&"y"===this.options.axis||(this.helper[0].style.left=this.position.left+"px"),this.options.axis&&"x"===this.options.axis||(this.helper[0].style.top=this.position.top+"px"),e.ui.ddmanager&&e.ui.ddmanager.drag(this,t),!1},_mouseStop:function(t){var i=this,s=!1;return e.ui.ddmanager&&!this.options.dropBehaviour&&(s=e.ui.ddmanager.drop(this,t)),this.dropped&&(s=this.dropped,this.dropped=!1),"original"!==this.options.helper||e.contains(this.element[0].ownerDocument,this.element[0])?("invalid"===this.options.revert&&!s||"valid"===this.options.revert&&s||this.options.revert===!0||e.isFunction(this.options.revert)&&this.options.revert.call(this.element,s)?e(this.helper).animate(this.originalPosition,parseInt(this.options.revertDuration,10),function(){i._trigger("stop",t)!==!1&&i._clear()}):this._trigger("stop",t)!==!1&&this._clear(),!1):!1},_mouseUp:function(t){return e("div.ui-draggable-iframeFix").each(function(){this.parentNode.removeChild(this)}),e.ui.ddmanager&&e.ui.ddmanager.dragStop(this,t),e.ui.mouse.prototype._mouseUp.call(this,t)},cancel:function(){return this.helper.is(".ui-draggable-dragging")?this._mouseUp({}):this._clear(),this},_getHandle:function(t){return this.options.handle?!!e(t.target).closest(this.element.find(this.options.handle)).length:!0},_createHelper:function(t){var i=this.options,s=e.isFunction(i.helper)?e(i.helper.apply(this.element[0],[t])):"clone"===i.helper?this.element.clone().removeAttr("id"):this.element;return s.parents("body").length||s.appendTo("parent"===i.appendTo?this.element[0].parentNode:i.appendTo),s[0]===this.element[0]||/(fixed|absolute)/.test(s.css("position"))||s.css("position","absolute"),s},_adjustOffsetFromHelper:function(t){"string"==typeof t&&(t=t.split(" ")),e.isArray(t)&&(t={left:+t[0],top:+t[1]||0}),"left"in t&&(this.offset.click.left=t.left+this.margins.left),"right"in t&&(this.offset.click.left=this.helperProportions.width-t.right+this.margins.left),"top"in t&&(this.offset.click.top=t.top+this.margins.top),"bottom"in t&&(this.offset.click.top=this.helperProportions.height-t.bottom+this.margins.top)},_getParentOffset:function(){var t=this.offsetParent.offset();return"absolute"===this.cssPosition&&this.scrollParent[0]!==document&&e.contains(this.scrollParent[0],this.offsetParent[0])&&(t.left+=this.scrollParent.scrollLeft(),t.top+=this.scrollParent.scrollTop()),(this.offsetParent[0]===document.body||this.offsetParent[0].tagName&&"html"===this.offsetParent[0].tagName.toLowerCase()&&e.ui.ie)&&(t={top:0,left:0}),{top:t.top+(parseInt(this.offsetParent.css("borderTopWidth"),10)||0),left:t.left+(parseInt(this.offsetParent.css("borderLeftWidth"),10)||0)}},_getRelativeOffset:function(){if("relative"===this.cssPosition){var e=this.element.position();return{top:e.top-(parseInt(this.helper.css("top"),10)||0)+this.scrollParent.scrollTop(),left:e.left-(parseInt(this.helper.css("left"),10)||0)+this.scrollParent.scrollLeft()}}return{top:0,left:0}},_cacheMargins:function(){this.margins={left:parseInt(this.element.css("marginLeft"),10)||0,top:parseInt(this.element.css("marginTop"),10)||0,right:parseInt(this.element.css("marginRight"),10)||0,bottom:parseInt(this.element.css("marginBottom"),10)||0}},_cacheHelperProportions:function(){this.helperProportions={width:this.helper.outerWidth(),height:this.helper.outerHeight()}},_setContainment:function(){var t,i,s,n=this.options;return n.containment?"window"===n.containment?(this.containment=[e(window).scrollLeft()-this.offset.relative.left-this.offset.parent.left,e(window).scrollTop()-this.offset.relative.top-this.offset.parent.top,e(window).scrollLeft()+e(window).width()-this.helperProportions.width-this.margins.left,e(window).scrollTop()+(e(window).height()||document.body.parentNode.scrollHeight)-this.helperProportions.height-this.margins.top],undefined):"document"===n.containment?(this.containment=[0,0,e(document).width()-this.helperProportions.width-this.margins.left,(e(document).height()||document.body.parentNode.scrollHeight)-this.helperProportions.height-this.margins.top],undefined):n.containment.constructor===Array?(this.containment=n.containment,undefined):("parent"===n.containment&&(n.containment=this.helper[0].parentNode),i=e(n.containment),s=i[0],s&&(t="hidden"!==i.css("overflow"),this.containment=[(parseInt(i.css("borderLeftWidth"),10)||0)+(parseInt(i.css("paddingLeft"),10)||0),(parseInt(i.css("borderTopWidth"),10)||0)+(parseInt(i.css("paddingTop"),10)||0),(t?Math.max(s.scrollWidth,s.offsetWidth):s.offsetWidth)-(parseInt(i.css("borderRightWidth"),10)||0)-(parseInt(i.css("paddingRight"),10)||0)-this.helperProportions.width-this.margins.left-this.margins.right,(t?Math.max(s.scrollHeight,s.offsetHeight):s.offsetHeight)-(parseInt(i.css("borderBottomWidth"),10)||0)-(parseInt(i.css("paddingBottom"),10)||0)-this.helperProportions.height-this.margins.top-this.margins.bottom],this.relative_container=i),undefined):(this.containment=null,undefined)},_convertPositionTo:function(t,i){i||(i=this.position);var s="absolute"===t?1:-1,n="absolute"!==this.cssPosition||this.scrollParent[0]!==document&&e.contains(this.scrollParent[0],this.offsetParent[0])?this.scrollParent:this.offsetParent;return this.offset.scroll||(this.offset.scroll={top:n.scrollTop(),left:n.scrollLeft()}),{top:i.top+this.offset.relative.top*s+this.offset.parent.top*s-("fixed"===this.cssPosition?-this.scrollParent.scrollTop():this.offset.scroll.top)*s,left:i.left+this.offset.relative.left*s+this.offset.parent.left*s-("fixed"===this.cssPosition?-this.scrollParent.scrollLeft():this.offset.scroll.left)*s}},_generatePosition:function(t){var i,s,n,a,o=this.options,r="absolute"!==this.cssPosition||this.scrollParent[0]!==document&&e.contains(this.scrollParent[0],this.offsetParent[0])?this.scrollParent:this.offsetParent,h=t.pageX,l=t.pageY;return this.offset.scroll||(this.offset.scroll={top:r.scrollTop(),left:r.scrollLeft()}),this.originalPosition&&(this.containment&&(this.relative_container?(s=this.relative_container.offset(),i=[this.containment[0]+s.left,this.containment[1]+s.top,this.containment[2]+s.left,this.containment[3]+s.top]):i=this.containment,t.pageX-this.offset.click.left<i[0]&&(h=i[0]+this.offset.click.left),t.pageY-this.offset.click.top<i[1]&&(l=i[1]+this.offset.click.top),t.pageX-this.offset.click.left>i[2]&&(h=i[2]+this.offset.click.left),t.pageY-this.offset.click.top>i[3]&&(l=i[3]+this.offset.click.top)),o.grid&&(n=o.grid[1]?this.originalPageY+Math.round((l-this.originalPageY)/o.grid[1])*o.grid[1]:this.originalPageY,l=i?n-this.offset.click.top>=i[1]||n-this.offset.click.top>i[3]?n:n-this.offset.click.top>=i[1]?n-o.grid[1]:n+o.grid[1]:n,a=o.grid[0]?this.originalPageX+Math.round((h-this.originalPageX)/o.grid[0])*o.grid[0]:this.originalPageX,h=i?a-this.offset.click.left>=i[0]||a-this.offset.click.left>i[2]?a:a-this.offset.click.left>=i[0]?a-o.grid[0]:a+o.grid[0]:a)),{top:l-this.offset.click.top-this.offset.relative.top-this.offset.parent.top+("fixed"===this.cssPosition?-this.scrollParent.scrollTop():this.offset.scroll.top),left:h-this.offset.click.left-this.offset.relative.left-this.offset.parent.left+("fixed"===this.cssPosition?-this.scrollParent.scrollLeft():this.offset.scroll.left)}},_clear:function(){this.helper.removeClass("ui-draggable-dragging"),this.helper[0]===this.element[0]||this.cancelHelperRemoval||this.helper.remove(),this.helper=null,this.cancelHelperRemoval=!1},_trigger:function(t,i,s){return s=s||this._uiHash(),e.ui.plugin.call(this,t,[i,s]),"drag"===t&&(this.positionAbs=this._convertPositionTo("absolute")),e.Widget.prototype._trigger.call(this,t,i,s)},plugins:{},_uiHash:function(){return{helper:this.helper,position:this.position,originalPosition:this.originalPosition,offset:this.positionAbs}}}),e.ui.plugin.add("draggable","connectToSortable",{start:function(t,i){var s=e(this).data("ui-draggable"),n=s.options,a=e.extend({},i,{item:s.element});s.sortables=[],e(n.connectToSortable).each(function(){var i=e.data(this,"ui-sortable");i&&!i.options.disabled&&(s.sortables.push({instance:i,shouldRevert:i.options.revert}),i.refreshPositions(),i._trigger("activate",t,a))})},stop:function(t,i){var s=e(this).data("ui-draggable"),n=e.extend({},i,{item:s.element});e.each(s.sortables,function(){this.instance.isOver?(this.instance.isOver=0,s.cancelHelperRemoval=!0,this.instance.cancelHelperRemoval=!1,this.shouldRevert&&(this.instance.options.revert=this.shouldRevert),this.instance._mouseStop(t),this.instance.options.helper=this.instance.options._helper,"original"===s.options.helper&&this.instance.currentItem.css({top:"auto",left:"auto"})):(this.instance.cancelHelperRemoval=!1,this.instance._trigger("deactivate",t,n))})},drag:function(t,i){var s=e(this).data("ui-draggable"),n=this;e.each(s.sortables,function(){var a=!1,o=this;this.instance.positionAbs=s.positionAbs,this.instance.helperProportions=s.helperProportions,this.instance.offset.click=s.offset.click,this.instance._intersectsWith(this.instance.containerCache)&&(a=!0,e.each(s.sortables,function(){return this.instance.positionAbs=s.positionAbs,this.instance.helperProportions=s.helperProportions,this.instance.offset.click=s.offset.click,this!==o&&this.instance._intersectsWith(this.instance.containerCache)&&e.contains(o.instance.element[0],this.instance.element[0])&&(a=!1),a})),a?(this.instance.isOver||(this.instance.isOver=1,this.instance.currentItem=e(n).clone().removeAttr("id").appendTo(this.instance.element).data("ui-sortable-item",!0),this.instance.options._helper=this.instance.options.helper,this.instance.options.helper=function(){return i.helper[0]},t.target=this.instance.currentItem[0],this.instance._mouseCapture(t,!0),this.instance._mouseStart(t,!0,!0),this.instance.offset.click.top=s.offset.click.top,this.instance.offset.click.left=s.offset.click.left,this.instance.offset.parent.left-=s.offset.parent.left-this.instance.offset.parent.left,this.instance.offset.parent.top-=s.offset.parent.top-this.instance.offset.parent.top,s._trigger("toSortable",t),s.dropped=this.instance.element,s.currentItem=s.element,this.instance.fromOutside=s),this.instance.currentItem&&this.instance._mouseDrag(t)):this.instance.isOver&&(this.instance.isOver=0,this.instance.cancelHelperRemoval=!0,this.instance.options.revert=!1,this.instance._trigger("out",t,this.instance._uiHash(this.instance)),this.instance._mouseStop(t,!0),this.instance.options.helper=this.instance.options._helper,this.instance.currentItem.remove(),this.instance.placeholder&&this.instance.placeholder.remove(),s._trigger("fromSortable",t),s.dropped=!1)})}}),e.ui.plugin.add("draggable","cursor",{start:function(){var t=e("body"),i=e(this).data("ui-draggable").options;t.css("cursor")&&(i._cursor=t.css("cursor")),t.css("cursor",i.cursor)},stop:function(){var t=e(this).data("ui-draggable").options;t._cursor&&e("body").css("cursor",t._cursor)}}),e.ui.plugin.add("draggable","opacity",{start:function(t,i){var s=e(i.helper),n=e(this).data("ui-draggable").options;s.css("opacity")&&(n._opacity=s.css("opacity")),s.css("opacity",n.opacity)},stop:function(t,i){var s=e(this).data("ui-draggable").options;s._opacity&&e(i.helper).css("opacity",s._opacity)}}),e.ui.plugin.add("draggable","scroll",{start:function(){var t=e(this).data("ui-draggable");t.scrollParent[0]!==document&&"HTML"!==t.scrollParent[0].tagName&&(t.overflowOffset=t.scrollParent.offset())},drag:function(t){var i=e(this).data("ui-draggable"),s=i.options,n=!1;i.scrollParent[0]!==document&&"HTML"!==i.scrollParent[0].tagName?(s.axis&&"x"===s.axis||(i.overflowOffset.top+i.scrollParent[0].offsetHeight-t.pageY<s.scrollSensitivity?i.scrollParent[0].scrollTop=n=i.scrollParent[0].scrollTop+s.scrollSpeed:t.pageY-i.overflowOffset.top<s.scrollSensitivity&&(i.scrollParent[0].scrollTop=n=i.scrollParent[0].scrollTop-s.scrollSpeed)),s.axis&&"y"===s.axis||(i.overflowOffset.left+i.scrollParent[0].offsetWidth-t.pageX<s.scrollSensitivity?i.scrollParent[0].scrollLeft=n=i.scrollParent[0].scrollLeft+s.scrollSpeed:t.pageX-i.overflowOffset.left<s.scrollSensitivity&&(i.scrollParent[0].scrollLeft=n=i.scrollParent[0].scrollLeft-s.scrollSpeed))):(s.axis&&"x"===s.axis||(t.pageY-e(document).scrollTop()<s.scrollSensitivity?n=e(document).scrollTop(e(document).scrollTop()-s.scrollSpeed):e(window).height()-(t.pageY-e(document).scrollTop())<s.scrollSensitivity&&(n=e(document).scrollTop(e(document).scrollTop()+s.scrollSpeed))),s.axis&&"y"===s.axis||(t.pageX-e(document).scrollLeft()<s.scrollSensitivity?n=e(document).scrollLeft(e(document).scrollLeft()-s.scrollSpeed):e(window).width()-(t.pageX-e(document).scrollLeft())<s.scrollSensitivity&&(n=e(document).scrollLeft(e(document).scrollLeft()+s.scrollSpeed)))),n!==!1&&e.ui.ddmanager&&!s.dropBehaviour&&e.ui.ddmanager.prepareOffsets(i,t)}}),e.ui.plugin.add("draggable","snap",{start:function(){var t=e(this).data("ui-draggable"),i=t.options;t.snapElements=[],e(i.snap.constructor!==String?i.snap.items||":data(ui-draggable)":i.snap).each(function(){var i=e(this),s=i.offset();this!==t.element[0]&&t.snapElements.push({item:this,width:i.outerWidth(),height:i.outerHeight(),top:s.top,left:s.left})})},drag:function(t,i){var s,n,a,o,r,h,l,u,c,d,p=e(this).data("ui-draggable"),f=p.options,m=f.snapTolerance,g=i.offset.left,v=g+p.helperProportions.width,b=i.offset.top,y=b+p.helperProportions.height;for(c=p.snapElements.length-1;c>=0;c--)r=p.snapElements[c].left,h=r+p.snapElements[c].width,l=p.snapElements[c].top,u=l+p.snapElements[c].height,r-m>v||g>h+m||l-m>y||b>u+m||!e.contains(p.snapElements[c].item.ownerDocument,p.snapElements[c].item)?(p.snapElements[c].snapping&&p.options.snap.release&&p.options.snap.release.call(p.element,t,e.extend(p._uiHash(),{snapItem:p.snapElements[c].item})),p.snapElements[c].snapping=!1):("inner"!==f.snapMode&&(s=m>=Math.abs(l-y),n=m>=Math.abs(u-b),a=m>=Math.abs(r-v),o=m>=Math.abs(h-g),s&&(i.position.top=p._convertPositionTo("relative",{top:l-p.helperProportions.height,left:0}).top-p.margins.top),n&&(i.position.top=p._convertPositionTo("relative",{top:u,left:0}).top-p.margins.top),a&&(i.position.left=p._convertPositionTo("relative",{top:0,left:r-p.helperProportions.width}).left-p.margins.left),o&&(i.position.left=p._convertPositionTo("relative",{top:0,left:h}).left-p.margins.left)),d=s||n||a||o,"outer"!==f.snapMode&&(s=m>=Math.abs(l-b),n=m>=Math.abs(u-y),a=m>=Math.abs(r-g),o=m>=Math.abs(h-v),s&&(i.position.top=p._convertPositionTo("relative",{top:l,left:0}).top-p.margins.top),n&&(i.position.top=p._convertPositionTo("relative",{top:u-p.helperProportions.height,left:0}).top-p.margins.top),a&&(i.position.left=p._convertPositionTo("relative",{top:0,left:r}).left-p.margins.left),o&&(i.position.left=p._convertPositionTo("relative",{top:0,left:h-p.helperProportions.width}).left-p.margins.left)),!p.snapElements[c].snapping&&(s||n||a||o||d)&&p.options.snap.snap&&p.options.snap.snap.call(p.element,t,e.extend(p._uiHash(),{snapItem:p.snapElements[c].item})),p.snapElements[c].snapping=s||n||a||o||d)}}),e.ui.plugin.add("draggable","stack",{start:function(){var t,i=this.data("ui-draggable").options,s=e.makeArray(e(i.stack)).sort(function(t,i){return(parseInt(e(t).css("zIndex"),10)||0)-(parseInt(e(i).css("zIndex"),10)||0)});s.length&&(t=parseInt(e(s[0]).css("zIndex"),10)||0,e(s).each(function(i){e(this).css("zIndex",t+i)}),this.css("zIndex",t+s.length))}}),e.ui.plugin.add("draggable","zIndex",{start:function(t,i){var s=e(i.helper),n=e(this).data("ui-draggable").options;s.css("zIndex")&&(n._zIndex=s.css("zIndex")),s.css("zIndex",n.zIndex)},stop:function(t,i){var s=e(this).data("ui-draggable").options;s._zIndex&&e(i.helper).css("zIndex",s._zIndex)}})})(jQuery);(function(e){function t(e,t,i){return e>t&&t+i>e}e.widget("ui.droppable",{version:"1.10.3",widgetEventPrefix:"drop",options:{accept:"*",activeClass:!1,addClasses:!0,greedy:!1,hoverClass:!1,scope:"default",tolerance:"intersect",activate:null,deactivate:null,drop:null,out:null,over:null},_create:function(){var t=this.options,i=t.accept;this.isover=!1,this.isout=!0,this.accept=e.isFunction(i)?i:function(e){return e.is(i)},this.proportions={width:this.element[0].offsetWidth,height:this.element[0].offsetHeight},e.ui.ddmanager.droppables[t.scope]=e.ui.ddmanager.droppables[t.scope]||[],e.ui.ddmanager.droppables[t.scope].push(this),t.addClasses&&this.element.addClass("ui-droppable")},_destroy:function(){for(var t=0,i=e.ui.ddmanager.droppables[this.options.scope];i.length>t;t++)i[t]===this&&i.splice(t,1);this.element.removeClass("ui-droppable ui-droppable-disabled")},_setOption:function(t,i){"accept"===t&&(this.accept=e.isFunction(i)?i:function(e){return e.is(i)}),e.Widget.prototype._setOption.apply(this,arguments)},_activate:function(t){var i=e.ui.ddmanager.current;this.options.activeClass&&this.element.addClass(this.options.activeClass),i&&this._trigger("activate",t,this.ui(i))},_deactivate:function(t){var i=e.ui.ddmanager.current;this.options.activeClass&&this.element.removeClass(this.options.activeClass),i&&this._trigger("deactivate",t,this.ui(i))},_over:function(t){var i=e.ui.ddmanager.current;i&&(i.currentItem||i.element)[0]!==this.element[0]&&this.accept.call(this.element[0],i.currentItem||i.element)&&(this.options.hoverClass&&this.element.addClass(this.options.hoverClass),this._trigger("over",t,this.ui(i)))},_out:function(t){var i=e.ui.ddmanager.current;i&&(i.currentItem||i.element)[0]!==this.element[0]&&this.accept.call(this.element[0],i.currentItem||i.element)&&(this.options.hoverClass&&this.element.removeClass(this.options.hoverClass),this._trigger("out",t,this.ui(i)))},_drop:function(t,i){var s=i||e.ui.ddmanager.current,n=!1;return s&&(s.currentItem||s.element)[0]!==this.element[0]?(this.element.find(":data(ui-droppable)").not(".ui-draggable-dragging").each(function(){var t=e.data(this,"ui-droppable");return t.options.greedy&&!t.options.disabled&&t.options.scope===s.options.scope&&t.accept.call(t.element[0],s.currentItem||s.element)&&e.ui.intersect(s,e.extend(t,{offset:t.element.offset()}),t.options.tolerance)?(n=!0,!1):undefined}),n?!1:this.accept.call(this.element[0],s.currentItem||s.element)?(this.options.activeClass&&this.element.removeClass(this.options.activeClass),this.options.hoverClass&&this.element.removeClass(this.options.hoverClass),this._trigger("drop",t,this.ui(s)),this.element):!1):!1},ui:function(e){return{draggable:e.currentItem||e.element,helper:e.helper,position:e.position,offset:e.positionAbs}}}),e.ui.intersect=function(e,i,s){if(!i.offset)return!1;var n,a,o=(e.positionAbs||e.position.absolute).left,r=o+e.helperProportions.width,h=(e.positionAbs||e.position.absolute).top,l=h+e.helperProportions.height,u=i.offset.left,c=u+i.proportions.width,d=i.offset.top,p=d+i.proportions.height;switch(s){case"fit":return o>=u&&c>=r&&h>=d&&p>=l;case"intersect":return o+e.helperProportions.width/2>u&&c>r-e.helperProportions.width/2&&h+e.helperProportions.height/2>d&&p>l-e.helperProportions.height/2;case"pointer":return n=(e.positionAbs||e.position.absolute).left+(e.clickOffset||e.offset.click).left,a=(e.positionAbs||e.position.absolute).top+(e.clickOffset||e.offset.click).top,t(a,d,i.proportions.height)&&t(n,u,i.proportions.width);case"touch":return(h>=d&&p>=h||l>=d&&p>=l||d>h&&l>p)&&(o>=u&&c>=o||r>=u&&c>=r||u>o&&r>c);default:return!1}},e.ui.ddmanager={current:null,droppables:{"default":[]},prepareOffsets:function(t,i){var s,n,a=e.ui.ddmanager.droppables[t.options.scope]||[],o=i?i.type:null,r=(t.currentItem||t.element).find(":data(ui-droppable)").addBack();e:for(s=0;a.length>s;s++)if(!(a[s].options.disabled||t&&!a[s].accept.call(a[s].element[0],t.currentItem||t.element))){for(n=0;r.length>n;n++)if(r[n]===a[s].element[0]){a[s].proportions.height=0;continue e}a[s].visible="none"!==a[s].element.css("display"),a[s].visible&&("mousedown"===o&&a[s]._activate.call(a[s],i),a[s].offset=a[s].element.offset(),a[s].proportions={width:a[s].element[0].offsetWidth,height:a[s].element[0].offsetHeight})}},drop:function(t,i){var s=!1;return e.each((e.ui.ddmanager.droppables[t.options.scope]||[]).slice(),function(){this.options&&(!this.options.disabled&&this.visible&&e.ui.intersect(t,this,this.options.tolerance)&&(s=this._drop.call(this,i)||s),!this.options.disabled&&this.visible&&this.accept.call(this.element[0],t.currentItem||t.element)&&(this.isout=!0,this.isover=!1,this._deactivate.call(this,i)))}),s},dragStart:function(t,i){t.element.parentsUntil("body").bind("scroll.droppable",function(){t.options.refreshPositions||e.ui.ddmanager.prepareOffsets(t,i)})},drag:function(t,i){t.options.refreshPositions&&e.ui.ddmanager.prepareOffsets(t,i),e.each(e.ui.ddmanager.droppables[t.options.scope]||[],function(){if(!this.options.disabled&&!this.greedyChild&&this.visible){var s,n,a,o=e.ui.intersect(t,this,this.options.tolerance),r=!o&&this.isover?"isout":o&&!this.isover?"isover":null;r&&(this.options.greedy&&(n=this.options.scope,a=this.element.parents(":data(ui-droppable)").filter(function(){return e.data(this,"ui-droppable").options.scope===n}),a.length&&(s=e.data(a[0],"ui-droppable"),s.greedyChild="isover"===r)),s&&"isover"===r&&(s.isover=!1,s.isout=!0,s._out.call(s,i)),this[r]=!0,this["isout"===r?"isover":"isout"]=!1,this["isover"===r?"_over":"_out"].call(this,i),s&&"isout"===r&&(s.isout=!1,s.isover=!0,s._over.call(s,i)))}})},dragStop:function(t,i){t.element.parentsUntil("body").unbind("scroll.droppable"),t.options.refreshPositions||e.ui.ddmanager.prepareOffsets(t,i)}}})(jQuery);(function(e){function t(e){return parseInt(e,10)||0}function i(e){return!isNaN(parseInt(e,10))}e.widget("ui.resizable",e.ui.mouse,{version:"1.10.3",widgetEventPrefix:"resize",options:{alsoResize:!1,animate:!1,animateDuration:"slow",animateEasing:"swing",aspectRatio:!1,autoHide:!1,containment:!1,ghost:!1,grid:!1,handles:"e,s,se",helper:!1,maxHeight:null,maxWidth:null,minHeight:10,minWidth:10,zIndex:90,resize:null,start:null,stop:null},_create:function(){var t,i,s,n,a,o=this,r=this.options;if(this.element.addClass("ui-resizable"),e.extend(this,{_aspectRatio:!!r.aspectRatio,aspectRatio:r.aspectRatio,originalElement:this.element,_proportionallyResizeElements:[],_helper:r.helper||r.ghost||r.animate?r.helper||"ui-resizable-helper":null}),this.element[0].nodeName.match(/canvas|textarea|input|select|button|img/i)&&(this.element.wrap(e("<div class='ui-wrapper' style='overflow: hidden;'></div>").css({position:this.element.css("position"),width:this.element.outerWidth(),height:this.element.outerHeight(),top:this.element.css("top"),left:this.element.css("left")})),this.element=this.element.parent().data("ui-resizable",this.element.data("ui-resizable")),this.elementIsWrapper=!0,this.element.css({marginLeft:this.originalElement.css("marginLeft"),marginTop:this.originalElement.css("marginTop"),marginRight:this.originalElement.css("marginRight"),marginBottom:this.originalElement.css("marginBottom")}),this.originalElement.css({marginLeft:0,marginTop:0,marginRight:0,marginBottom:0}),this.originalResizeStyle=this.originalElement.css("resize"),this.originalElement.css("resize","none"),this._proportionallyResizeElements.push(this.originalElement.css({position:"static",zoom:1,display:"block"})),this.originalElement.css({margin:this.originalElement.css("margin")}),this._proportionallyResize()),this.handles=r.handles||(e(".ui-resizable-handle",this.element).length?{n:".ui-resizable-n",e:".ui-resizable-e",s:".ui-resizable-s",w:".ui-resizable-w",se:".ui-resizable-se",sw:".ui-resizable-sw",ne:".ui-resizable-ne",nw:".ui-resizable-nw"}:"e,s,se"),this.handles.constructor===String)for("all"===this.handles&&(this.handles="n,e,s,w,se,sw,ne,nw"),t=this.handles.split(","),this.handles={},i=0;t.length>i;i++)s=e.trim(t[i]),a="ui-resizable-"+s,n=e("<div class='ui-resizable-handle "+a+"'></div>"),n.css({zIndex:r.zIndex}),"se"===s&&n.addClass("ui-icon ui-icon-gripsmall-diagonal-se"),this.handles[s]=".ui-resizable-"+s,this.element.append(n);this._renderAxis=function(t){var i,s,n,a;t=t||this.element;for(i in this.handles)this.handles[i].constructor===String&&(this.handles[i]=e(this.handles[i],this.element).show()),this.elementIsWrapper&&this.originalElement[0].nodeName.match(/textarea|input|select|button/i)&&(s=e(this.handles[i],this.element),a=/sw|ne|nw|se|n|s/.test(i)?s.outerHeight():s.outerWidth(),n=["padding",/ne|nw|n/.test(i)?"Top":/se|sw|s/.test(i)?"Bottom":/^e$/.test(i)?"Right":"Left"].join(""),t.css(n,a),this._proportionallyResize()),e(this.handles[i]).length},this._renderAxis(this.element),this._handles=e(".ui-resizable-handle",this.element).disableSelection(),this._handles.mouseover(function(){o.resizing||(this.className&&(n=this.className.match(/ui-resizable-(se|sw|ne|nw|n|e|s|w)/i)),o.axis=n&&n[1]?n[1]:"se")}),r.autoHide&&(this._handles.hide(),e(this.element).addClass("ui-resizable-autohide").mouseenter(function(){r.disabled||(e(this).removeClass("ui-resizable-autohide"),o._handles.show())}).mouseleave(function(){r.disabled||o.resizing||(e(this).addClass("ui-resizable-autohide"),o._handles.hide())})),this._mouseInit()},_destroy:function(){this._mouseDestroy();var t,i=function(t){e(t).removeClass("ui-resizable ui-resizable-disabled ui-resizable-resizing").removeData("resizable").removeData("ui-resizable").unbind(".resizable").find(".ui-resizable-handle").remove()};return this.elementIsWrapper&&(i(this.element),t=this.element,this.originalElement.css({position:t.css("position"),width:t.outerWidth(),height:t.outerHeight(),top:t.css("top"),left:t.css("left")}).insertAfter(t),t.remove()),this.originalElement.css("resize",this.originalResizeStyle),i(this.originalElement),this},_mouseCapture:function(t){var i,s,n=!1;for(i in this.handles)s=e(this.handles[i])[0],(s===t.target||e.contains(s,t.target))&&(n=!0);return!this.options.disabled&&n},_mouseStart:function(i){var s,n,a,o=this.options,r=this.element.position(),h=this.element;return this.resizing=!0,/absolute/.test(h.css("position"))?h.css({position:"absolute",top:h.css("top"),left:h.css("left")}):h.is(".ui-draggable")&&h.css({position:"absolute",top:r.top,left:r.left}),this._renderProxy(),s=t(this.helper.css("left")),n=t(this.helper.css("top")),o.containment&&(s+=e(o.containment).scrollLeft()||0,n+=e(o.containment).scrollTop()||0),this.offset=this.helper.offset(),this.position={left:s,top:n},this.size=this._helper?{width:h.outerWidth(),height:h.outerHeight()}:{width:h.width(),height:h.height()},this.originalSize=this._helper?{width:h.outerWidth(),height:h.outerHeight()}:{width:h.width(),height:h.height()},this.originalPosition={left:s,top:n},this.sizeDiff={width:h.outerWidth()-h.width(),height:h.outerHeight()-h.height()},this.originalMousePosition={left:i.pageX,top:i.pageY},this.aspectRatio="number"==typeof o.aspectRatio?o.aspectRatio:this.originalSize.width/this.originalSize.height||1,a=e(".ui-resizable-"+this.axis).css("cursor"),e("body").css("cursor","auto"===a?this.axis+"-resize":a),h.addClass("ui-resizable-resizing"),this._propagate("start",i),!0},_mouseDrag:function(t){var i,s=this.helper,n={},a=this.originalMousePosition,o=this.axis,r=this.position.top,h=this.position.left,l=this.size.width,u=this.size.height,c=t.pageX-a.left||0,d=t.pageY-a.top||0,p=this._change[o];return p?(i=p.apply(this,[t,c,d]),this._updateVirtualBoundaries(t.shiftKey),(this._aspectRatio||t.shiftKey)&&(i=this._updateRatio(i,t)),i=this._respectSize(i,t),this._updateCache(i),this._propagate("resize",t),this.position.top!==r&&(n.top=this.position.top+"px"),this.position.left!==h&&(n.left=this.position.left+"px"),this.size.width!==l&&(n.width=this.size.width+"px"),this.size.height!==u&&(n.height=this.size.height+"px"),s.css(n),!this._helper&&this._proportionallyResizeElements.length&&this._proportionallyResize(),e.isEmptyObject(n)||this._trigger("resize",t,this.ui()),!1):!1},_mouseStop:function(t){this.resizing=!1;var i,s,n,a,o,r,h,l=this.options,u=this;return this._helper&&(i=this._proportionallyResizeElements,s=i.length&&/textarea/i.test(i[0].nodeName),n=s&&e.ui.hasScroll(i[0],"left")?0:u.sizeDiff.height,a=s?0:u.sizeDiff.width,o={width:u.helper.width()-a,height:u.helper.height()-n},r=parseInt(u.element.css("left"),10)+(u.position.left-u.originalPosition.left)||null,h=parseInt(u.element.css("top"),10)+(u.position.top-u.originalPosition.top)||null,l.animate||this.element.css(e.extend(o,{top:h,left:r})),u.helper.height(u.size.height),u.helper.width(u.size.width),this._helper&&!l.animate&&this._proportionallyResize()),e("body").css("cursor","auto"),this.element.removeClass("ui-resizable-resizing"),this._propagate("stop",t),this._helper&&this.helper.remove(),!1},_updateVirtualBoundaries:function(e){var t,s,n,a,o,r=this.options;o={minWidth:i(r.minWidth)?r.minWidth:0,maxWidth:i(r.maxWidth)?r.maxWidth:1/0,minHeight:i(r.minHeight)?r.minHeight:0,maxHeight:i(r.maxHeight)?r.maxHeight:1/0},(this._aspectRatio||e)&&(t=o.minHeight*this.aspectRatio,n=o.minWidth/this.aspectRatio,s=o.maxHeight*this.aspectRatio,a=o.maxWidth/this.aspectRatio,t>o.minWidth&&(o.minWidth=t),n>o.minHeight&&(o.minHeight=n),o.maxWidth>s&&(o.maxWidth=s),o.maxHeight>a&&(o.maxHeight=a)),this._vBoundaries=o},_updateCache:function(e){this.offset=this.helper.offset(),i(e.left)&&(this.position.left=e.left),i(e.top)&&(this.position.top=e.top),i(e.height)&&(this.size.height=e.height),i(e.width)&&(this.size.width=e.width)},_updateRatio:function(e){var t=this.position,s=this.size,n=this.axis;return i(e.height)?e.width=e.height*this.aspectRatio:i(e.width)&&(e.height=e.width/this.aspectRatio),"sw"===n&&(e.left=t.left+(s.width-e.width),e.top=null),"nw"===n&&(e.top=t.top+(s.height-e.height),e.left=t.left+(s.width-e.width)),e},_respectSize:function(e){var t=this._vBoundaries,s=this.axis,n=i(e.width)&&t.maxWidth&&t.maxWidth<e.width,a=i(e.height)&&t.maxHeight&&t.maxHeight<e.height,o=i(e.width)&&t.minWidth&&t.minWidth>e.width,r=i(e.height)&&t.minHeight&&t.minHeight>e.height,h=this.originalPosition.left+this.originalSize.width,l=this.position.top+this.size.height,u=/sw|nw|w/.test(s),c=/nw|ne|n/.test(s);return o&&(e.width=t.minWidth),r&&(e.height=t.minHeight),n&&(e.width=t.maxWidth),a&&(e.height=t.maxHeight),o&&u&&(e.left=h-t.minWidth),n&&u&&(e.left=h-t.maxWidth),r&&c&&(e.top=l-t.minHeight),a&&c&&(e.top=l-t.maxHeight),e.width||e.height||e.left||!e.top?e.width||e.height||e.top||!e.left||(e.left=null):e.top=null,e},_proportionallyResize:function(){if(this._proportionallyResizeElements.length){var e,t,i,s,n,a=this.helper||this.element;for(e=0;this._proportionallyResizeElements.length>e;e++){if(n=this._proportionallyResizeElements[e],!this.borderDif)for(this.borderDif=[],i=[n.css("borderTopWidth"),n.css("borderRightWidth"),n.css("borderBottomWidth"),n.css("borderLeftWidth")],s=[n.css("paddingTop"),n.css("paddingRight"),n.css("paddingBottom"),n.css("paddingLeft")],t=0;i.length>t;t++)this.borderDif[t]=(parseInt(i[t],10)||0)+(parseInt(s[t],10)||0);n.css({height:a.height()-this.borderDif[0]-this.borderDif[2]||0,width:a.width()-this.borderDif[1]-this.borderDif[3]||0})}}},_renderProxy:function(){var t=this.element,i=this.options;this.elementOffset=t.offset(),this._helper?(this.helper=this.helper||e("<div style='overflow:hidden;'></div>"),this.helper.addClass(this._helper).css({width:this.element.outerWidth()-1,height:this.element.outerHeight()-1,position:"absolute",left:this.elementOffset.left+"px",top:this.elementOffset.top+"px",zIndex:++i.zIndex}),this.helper.appendTo("body").disableSelection()):this.helper=this.element},_change:{e:function(e,t){return{width:this.originalSize.width+t}},w:function(e,t){var i=this.originalSize,s=this.originalPosition;return{left:s.left+t,width:i.width-t}},n:function(e,t,i){var s=this.originalSize,n=this.originalPosition;return{top:n.top+i,height:s.height-i}},s:function(e,t,i){return{height:this.originalSize.height+i}},se:function(t,i,s){return e.extend(this._change.s.apply(this,arguments),this._change.e.apply(this,[t,i,s]))},sw:function(t,i,s){return e.extend(this._change.s.apply(this,arguments),this._change.w.apply(this,[t,i,s]))},ne:function(t,i,s){return e.extend(this._change.n.apply(this,arguments),this._change.e.apply(this,[t,i,s]))},nw:function(t,i,s){return e.extend(this._change.n.apply(this,arguments),this._change.w.apply(this,[t,i,s]))}},_propagate:function(t,i){e.ui.plugin.call(this,t,[i,this.ui()]),"resize"!==t&&this._trigger(t,i,this.ui())},plugins:{},ui:function(){return{originalElement:this.originalElement,element:this.element,helper:this.helper,position:this.position,size:this.size,originalSize:this.originalSize,originalPosition:this.originalPosition}}}),e.ui.plugin.add("resizable","animate",{stop:function(t){var i=e(this).data("ui-resizable"),s=i.options,n=i._proportionallyResizeElements,a=n.length&&/textarea/i.test(n[0].nodeName),o=a&&e.ui.hasScroll(n[0],"left")?0:i.sizeDiff.height,r=a?0:i.sizeDiff.width,h={width:i.size.width-r,height:i.size.height-o},l=parseInt(i.element.css("left"),10)+(i.position.left-i.originalPosition.left)||null,u=parseInt(i.element.css("top"),10)+(i.position.top-i.originalPosition.top)||null;i.element.animate(e.extend(h,u&&l?{top:u,left:l}:{}),{duration:s.animateDuration,easing:s.animateEasing,step:function(){var s={width:parseInt(i.element.css("width"),10),height:parseInt(i.element.css("height"),10),top:parseInt(i.element.css("top"),10),left:parseInt(i.element.css("left"),10)};n&&n.length&&e(n[0]).css({width:s.width,height:s.height}),i._updateCache(s),i._propagate("resize",t)}})}}),e.ui.plugin.add("resizable","containment",{start:function(){var i,s,n,a,o,r,h,l=e(this).data("ui-resizable"),u=l.options,c=l.element,d=u.containment,p=d instanceof e?d.get(0):/parent/.test(d)?c.parent().get(0):d;p&&(l.containerElement=e(p),/document/.test(d)||d===document?(l.containerOffset={left:0,top:0},l.containerPosition={left:0,top:0},l.parentData={element:e(document),left:0,top:0,width:e(document).width(),height:e(document).height()||document.body.parentNode.scrollHeight}):(i=e(p),s=[],e(["Top","Right","Left","Bottom"]).each(function(e,n){s[e]=t(i.css("padding"+n))}),l.containerOffset=i.offset(),l.containerPosition=i.position(),l.containerSize={height:i.innerHeight()-s[3],width:i.innerWidth()-s[1]},n=l.containerOffset,a=l.containerSize.height,o=l.containerSize.width,r=e.ui.hasScroll(p,"left")?p.scrollWidth:o,h=e.ui.hasScroll(p)?p.scrollHeight:a,l.parentData={element:p,left:n.left,top:n.top,width:r,height:h}))},resize:function(t){var i,s,n,a,o=e(this).data("ui-resizable"),r=o.options,h=o.containerOffset,l=o.position,u=o._aspectRatio||t.shiftKey,c={top:0,left:0},d=o.containerElement;d[0]!==document&&/static/.test(d.css("position"))&&(c=h),l.left<(o._helper?h.left:0)&&(o.size.width=o.size.width+(o._helper?o.position.left-h.left:o.position.left-c.left),u&&(o.size.height=o.size.width/o.aspectRatio),o.position.left=r.helper?h.left:0),l.top<(o._helper?h.top:0)&&(o.size.height=o.size.height+(o._helper?o.position.top-h.top:o.position.top),u&&(o.size.width=o.size.height*o.aspectRatio),o.position.top=o._helper?h.top:0),o.offset.left=o.parentData.left+o.position.left,o.offset.top=o.parentData.top+o.position.top,i=Math.abs((o._helper?o.offset.left-c.left:o.offset.left-c.left)+o.sizeDiff.width),s=Math.abs((o._helper?o.offset.top-c.top:o.offset.top-h.top)+o.sizeDiff.height),n=o.containerElement.get(0)===o.element.parent().get(0),a=/relative|absolute/.test(o.containerElement.css("position")),n&&a&&(i-=o.parentData.left),i+o.size.width>=o.parentData.width&&(o.size.width=o.parentData.width-i,u&&(o.size.height=o.size.width/o.aspectRatio)),s+o.size.height>=o.parentData.height&&(o.size.height=o.parentData.height-s,u&&(o.size.width=o.size.height*o.aspectRatio))},stop:function(){var t=e(this).data("ui-resizable"),i=t.options,s=t.containerOffset,n=t.containerPosition,a=t.containerElement,o=e(t.helper),r=o.offset(),h=o.outerWidth()-t.sizeDiff.width,l=o.outerHeight()-t.sizeDiff.height;t._helper&&!i.animate&&/relative/.test(a.css("position"))&&e(this).css({left:r.left-n.left-s.left,width:h,height:l}),t._helper&&!i.animate&&/static/.test(a.css("position"))&&e(this).css({left:r.left-n.left-s.left,width:h,height:l})}}),e.ui.plugin.add("resizable","alsoResize",{start:function(){var t=e(this).data("ui-resizable"),i=t.options,s=function(t){e(t).each(function(){var t=e(this);t.data("ui-resizable-alsoresize",{width:parseInt(t.width(),10),height:parseInt(t.height(),10),left:parseInt(t.css("left"),10),top:parseInt(t.css("top"),10)})})};"object"!=typeof i.alsoResize||i.alsoResize.parentNode?s(i.alsoResize):i.alsoResize.length?(i.alsoResize=i.alsoResize[0],s(i.alsoResize)):e.each(i.alsoResize,function(e){s(e)})},resize:function(t,i){var s=e(this).data("ui-resizable"),n=s.options,a=s.originalSize,o=s.originalPosition,r={height:s.size.height-a.height||0,width:s.size.width-a.width||0,top:s.position.top-o.top||0,left:s.position.left-o.left||0},h=function(t,s){e(t).each(function(){var t=e(this),n=e(this).data("ui-resizable-alsoresize"),a={},o=s&&s.length?s:t.parents(i.originalElement[0]).length?["width","height"]:["width","height","top","left"];e.each(o,function(e,t){var i=(n[t]||0)+(r[t]||0);i&&i>=0&&(a[t]=i||null)}),t.css(a)})};"object"!=typeof n.alsoResize||n.alsoResize.nodeType?h(n.alsoResize):e.each(n.alsoResize,function(e,t){h(e,t)})},stop:function(){e(this).removeData("resizable-alsoresize")}}),e.ui.plugin.add("resizable","ghost",{start:function(){var t=e(this).data("ui-resizable"),i=t.options,s=t.size;t.ghost=t.originalElement.clone(),t.ghost.css({opacity:.25,display:"block",position:"relative",height:s.height,width:s.width,margin:0,left:0,top:0}).addClass("ui-resizable-ghost").addClass("string"==typeof i.ghost?i.ghost:""),t.ghost.appendTo(t.helper)},resize:function(){var t=e(this).data("ui-resizable");t.ghost&&t.ghost.css({position:"relative",height:t.size.height,width:t.size.width})},stop:function(){var t=e(this).data("ui-resizable");t.ghost&&t.helper&&t.helper.get(0).removeChild(t.ghost.get(0))}}),e.ui.plugin.add("resizable","grid",{resize:function(){var t=e(this).data("ui-resizable"),i=t.options,s=t.size,n=t.originalSize,a=t.originalPosition,o=t.axis,r="number"==typeof i.grid?[i.grid,i.grid]:i.grid,h=r[0]||1,l=r[1]||1,u=Math.round((s.width-n.width)/h)*h,c=Math.round((s.height-n.height)/l)*l,d=n.width+u,p=n.height+c,f=i.maxWidth&&d>i.maxWidth,m=i.maxHeight&&p>i.maxHeight,g=i.minWidth&&i.minWidth>d,v=i.minHeight&&i.minHeight>p;i.grid=r,g&&(d+=h),v&&(p+=l),f&&(d-=h),m&&(p-=l),/^(se|s|e)$/.test(o)?(t.size.width=d,t.size.height=p):/^(ne)$/.test(o)?(t.size.width=d,t.size.height=p,t.position.top=a.top-c):/^(sw)$/.test(o)?(t.size.width=d,t.size.height=p,t.position.left=a.left-u):(t.size.width=d,t.size.height=p,t.position.top=a.top-c,t.position.left=a.left-u)}})})(jQuery);
var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    function parseTime(string) {
        var time = moment(string);
        if (time.isValid()) {
            return time;
        }
        return moment(string, "HH:mm:ss");
    }

    ns.TimeSlot = Backbone.Model.extend({

        defaults: {
            "resource": null,
            "start_time": null,
            "end_time": null,
            "organisation": null,
            "person": null,
            "status": "Unknown",
            "label": ""
        },

        parse: function (attributes) {

            if (attributes) {
                var data = _.clone(attributes);
                if (data.start_time) {
                    data.start_time = parseTime(data.start_time);
                }
                if (data.end_time) {
                    data.end_time = parseTime(data.end_time);
                }
                return data;
            }
            return null;
        },

        constructor: function (attributes, options) {
            Backbone.Model.apply(this, [this.parse(attributes), options]);
        },

        getDisplayName: function () {
            if (this.has("display_name")) {
                return this.get("display_name");
            } else {
                return this.getAktorName();
            }
        },

        getAktorName: function(){
            if (this.has("organisation") && this.get("organisation").name) {
                return this.get("organisation").name;
            } else if (this.has("person") && (this.get("person") instanceof Backbone.Model) && this.get("person").has("name")) {
                return this.get("person").get("name");
            } else if (this.has("person") && this.get("person").name) {
                return this.get("person").name;
            } else if (this.has("person") && this.get("person").first_name && this.get("person").last_name) {
                return this.get("person").last_name + ", " + this.get("person").first_name;
            }
            return "";
        },

        getStatus: function () {
            return this.get("status").toLowerCase();
        },

        getLabel: function() {
            if (this.get("status") == "Unknown"){
                return "";
            }

            var label = (this.has("display_name")) ? this.get("display_name").split('(')[0] : this.getAktorName();
            return label;
        },

        getRange: function () {
            return moment().range(this.get("start_time"), moment(this.get("end_time")));
        },

        toJSON: function () {
            var attributes = Backbone.Model.prototype.toJSON.apply(this, arguments);
            attributes.start_time = moment(this.get("start_time")).format("YYYY-MM-DDTHH:mm:ss");
            attributes.end_time = moment(this.get("end_time")).format("YYYY-MM-DDTHH:mm:ss");

            if (this.get("person") instanceof Backbone.Model) {
                attributes.person = {"uri": this.get("person").get("uri")};
            } else {
                attributes.person = {"uri": this.get("person").uri};
            }

            attributes.resource = {"uri": this.get("resource").uri};
            if (attributes.organisation) {
                if (!attributes.organisation.uri) {
                    attributes = _.omit(attributes, "organisation");
                }
            }

            return _.omit(attributes, "editable");
        },

        changeDate: function (date) {
            this.get("start_time").year(date.year()).month(date.month()).date(date.date());
            this.get("end_time").year(date.year()).month(date.month()).date(date.date());
            return this;
        },

        getDuration: function () {
            return this.get("end_time").diff(this.get("start_time"), "minutes");
        },

        collidesWith: function (timeSlot, own) {

            if (_.isEqual(this, timeSlot)) {                
                return false;
            }

            var range = this.getRange();
            if (range.contains(timeSlot.get("start_time"))) {
                return !(this.get("end_time").isSame(timeSlot.get("start_time")));
            }
            if (range.contains(timeSlot.get("end_time"))) {
                return !(this.get("start_time").isSame(timeSlot.get("end_time")));
            }
            if (!own) {
                return timeSlot.collidesWith(this, true);
            }
            return false;
        }
    });

}(Flod));
var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    function checkResize(el, ui) {
        var parent = $($(el).parent().parent());
        var max = parent.position().left + parent.width() - 25;
        var width = ui.position.left + ui.size.width;
        if (width >= max) {
            $(el).resizable("option", {"maxWidth": ui.size.width});
        }
    }

    var SlotView = Backbone.View.extend({

        className: "timeslot",

        events: {
            "click": "clicked"
        },

        initialize: function () {
            this.model.on("change:display_name", this.render, this);
            _.bindAll(this, "clicked");
            this.model.on("change:selected", this.render, this);
            this.model.on("change:status", this.render, this);
        },

        render: function () {
            var colspan = (this.model.getDuration() / this.model.collection.options.slot_duration);
            this.$el.data("slot", this.model);
            if (this.model.hasChanged("status")) {
                this.$el.removeClass(this.model.previous("status").toLowerCase());
            }
            this.$el.addClass(this.model.getStatus());

            if (this.model.has("color")) {
                this.$el.css("background-color", this.model.get("color"));
            }

            this.$el.text(this.model.getLabel());
            this.$el.attr("title", this.model.getDisplayName());

            var width = (colspan * 26) + ((2 * colspan) - 1);
            this.$el.css("width", width + "px");

            if (this.model.get("editable")) {
                this.makeEditable();
            } else {
                if (this.$el.is('.ui-resizable')) {
                    this.$el.resizable("destroy");
                }
                if (this.$el.is('.ui-draggable')) {
                    this.$el.draggable("destroy");
                }
            }
            if (this.model.get("selected")) {
                this.$el.addClass("selected");
            } else {
                this.$el.removeClass("selected");
            }
            return this;
        },

        resized: function (event, ui) {
            var diff = ((ui.size.width - ui.originalSize.width) / 28) * 30;
            if (this.model.collection.canChangeSlotTo(this.model, moment(this.model.get("start_time")), moment(this.model.get("end_time")).add(diff, "minutes"))) {
                this.model.get("end_time").add(diff, "minutes");
            }
            this.model.trigger("slotChanged", this.model);
        },

        makeEditable: function () {

            var resized = _.bind(this.resized, this);

            var tbody;
            if (this.options.table) {
                tbody = this.options.table.$("tbody");
            }
            this.$el.draggable({
                grid: [28, 26],
                zIndex: 100,
                containment: tbody
            }).resizable({
                "grid": [28, 26],
                "handles": "e",
                start: function (event, ui) {
                    checkResize(this, ui);
                },
                stop: function (event, ui) {
                    $(this).resizable("option", {"maxWidth": null});
                    resized(event, ui);
                },
                resize: function (event, ui) {
                    checkResize(this, ui);
                    $(this).css('height', '');
                }
            });
        },

        clicked: function () {
            var coll = this.model.collection;
            if (_.has(this.model, "parentCollection")) {
                // Trigger click event on parent
                coll = this.model.parentCollection;
            }
            coll.trigger("slotClick", this.model);
        }

    });

    ns.TimeSlotView = Backbone.View.extend({

        className: "slot",

        tagName: "td",

        render: function () {
            var colspan = (this.model.getDuration() / this.options.slotDuration);
            this.slotView = new SlotView({"model": this.model, "table": this.options.table});
            this.$el.append(this.slotView.render(colspan).$el);
            this.$el.attr("colspan", colspan);
            return this;
        }
    });

}(Flod));

var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.CalendarModel = Backbone.Model.extend({

        defaults: {
            "slot_duration": 30,
            "calendar_start": moment("08:00", "HH:mm"),
            "calendar_end": moment("23:00", "HH:mm"),
            "editable": false
        },

        constructor: function(attributes, options) {
            var rows = [];
            if (attributes) {
                rows = attributes.rows;
            }
            Backbone.Model.apply(this, [_.omit(attributes, "rows"), options]);
            this.set({"rows": this.mapRows(rows)});
            _.each(this.get("rows"), this.registerRow, this);
        },

        registerRow: function (row) {
            row.on("emptySlotClick", this.clickEmptySlot, this);
            row.on("slotClick", this.clickSlot, this);
            row.on("slotChanged", this.slotChanged, this);
            row.on("destroy", this.removeRow, this);
            row.on("add", this.addToRow, this);
        },

        addToRow: function (e) {
            this.trigger("slotAdded", e);
        },

        clickEmptySlot: function (e) {
            this.trigger("emptySlotClick", e);
        },

        clickSlot: function (e) {
            this.trigger("slotClick", e);
        },

        slotChanged: function (e) {
            this.trigger("slotChanged", e);
        },

        removeRow: function (row) {
            row.off("emptySlotClick", this.clickEmptySlot, this);
            row.off("slotClick", this.clickSlot, this);
            row.off("slotChanged", this.slotChanged, this);
            row.off("destroy", this.removeRow, this);
            var rows = _.without(this.get("rows"), row);
            this.set("rows", rows);
            this.trigger("reset");
        },

        mapRows: function (rowData) {

            var config = this.getConfig();
            return _.map(rowData, function (row) {
                if (row instanceof ns.CalendarRow) {
                    row.options = _.extend(row.options, config);
                    return row;
                }
                return new ns.CalendarRow(
                    row.slots,
                    _.omit(_.extend(row, config), "slots")
                );
            });
        },

        getConfig: function () {
            return {
                "slot_duration": this.get("slot_duration"),
                "calendar_start": this.get("calendar_start"),
                "calendar_end": this.get("calendar_end"),
                "editable": this.get("editable")
            };
        },

        row: function (index) {
            return this.get("rows")[index];
        },

        reset: function (rows) {
            rows = rows || [];
            this.set({"rows": this.mapRows(rows)});
            _.each(this.get("rows"), this.registerRow, this);
            this.trigger("reset");
        },

        getSlots: function () {
            return _.flatten(_.map(this.get("rows"), function (row) {
                return row.models;
            }));
        },

        addRow: function (row, index) {
            row =  this.mapRows([row])[0];

            if (!index) {
                this.get("rows").push(row);
            } else {
                this.get("rows").splice(index, 0, row);
            }
            this.registerRow(row);
            this.trigger("reset");
            return row;
        },

        addRows: function (rows) {
            if (!_.isArray(rows)) {
                rows = [rows];
            }
            rows =  this.mapRows(rows);
            var existing = this.get("rows");
            this.set("rows", existing.concat(rows));
            _.each(this.get("rows"), this.registerRow, this);
            this.trigger("reset");
            return rows;
        },

        getIndexForRow: function (row) {
            return _.indexOf(this.get("rows"), row);
        },

        getRowForDate: function (date) {
            return _.find(this.get("rows"), function (row) {
                return row.date.isSame(moment(date), "day");
            });
        },

        getRowForWeekday: function (weekday) {
            return _.find(this.get("rows"), function (row) {
                return row.date.isoWeekday() == weekday;
            });
        }
    });

}(Flod));
var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    function parseTime(string) {
        var time = moment(string);
        if (time.isValid()) {
            return time;
        }
        return moment(string, "HH:mm:ss");
    }

    ns.ColorSlot = Backbone.Model.extend({
        defaults: {
            "start_time": null,
            "end_time": null,
            "background_color": "#FFFFFF"
        },
        parse: function (attributes) {
            if (attributes) {
                var data = _.clone(attributes);
                if (data.start_time) {
                    data.start_time = parseTime(data.start_time);
                }
                if (data.end_time) {
                    data.end_time = parseTime(data.end_time);
                }
                return data;
            }
            return null;
        }
    });

    var ColorRow = Backbone.Collection.extend({
        model: ns.ColorSlot,
        getByTime: function (time) {
            return this.find(function (slot) {
                var start_time = moment(slot.get("start_time").format("HH:mm"), "HH:mm");
                var end_time = moment(slot.get("end_time").format("HH:mm"), "HH:mm");
                return ((start_time.isBefore(time) || start_time.isSame(time)) && end_time.isAfter(time));
            });
        }
    });

    ns.CalendarRow = Backbone.Collection.extend({

        model: ns.TimeSlot,

        initialize: function (models, options) {
            this.displayName = options.displayName;
            this.date = moment(options.date);
            this.options = _.omit(options, "displayName", "date");
            this.colors = new ColorRow(this.options.colors || [], {parse: true});
        },

        reset: function (models, options) {
            Backbone.Collection.prototype.reset.apply(this, arguments);
            this.each(this.checkEditable, this);
            return this;
        },

        removeSlot: function (slot) {
            this.remove(slot);
            this.trigger("slotRemoved");
        },

        getDisplayName: function () {
            return this.displayName || "";
        },

        getDate: function () {
            return this.date;
        },

        checkEditable: function (slot) {
            if (_.isUndefined(slot.get("editable")) || slot.get("editable")) {
                slot.set({"editable": this.options.editable});
            }
        },

        slotCollides: function (slot) {

            var collisions = this.map(function (existing) {
                return existing.collidesWith(slot);
            });
            return collisions.indexOf(true) !== -1;
        },

        canChangeSlotTo: function (slot, start_time, end_time) {

            if (this.onlyOwn && (slot.collection !== this)) {
                return false;
            }

            var cloned = slot.clone();

            var start = moment(this.date)
                .hours(start_time.hours())
                .minutes(start_time.minutes());

            var end = moment(this.date)
                .hours(end_time.hours())
                .minutes(end_time.minutes());

            cloned.set({"start_time": start});
            cloned.set({"end_time": end});

            //check if it is a conflict slot and compare with slots on parent row
            if (this.onlyOwn && slot.parentCollection){

                var collidesWithOtherSlots = false;

                for (var i in slot.parentCollection.models) {
                    var parentRowSlot = slot.parentCollection.models[i];
                    if (parentRowSlot.collidesWith(cloned)){

                        collidesWithOtherSlots = _.flatten(_.filter(parentRowSlot.get('slots'), function (sl) {
                            return (sl.cid == slot.cid);
                        }, this)).length == 0;

                        if (collidesWithOtherSlots){
                            break;
                        }
                    }
                }

                return !collidesWithOtherSlots;
            }

            if (this.slotCollides(cloned)) {

                var collisions = this.filter(function (existing) {
                    return existing.collidesWith(cloned);
                });
                if (collisions.length < 2) {
                    return _.isEqual(collisions[0], slot);
                } else {
                    return false;
                }
            }
            return true;
        },


        addColors: function (slots) {
            var status = _.map(slots, function (slot) {
                this.addColor(slot);
            }, this);
            return (status.indexOf(false) === -1);
        },

        addColor: function (slot) {
            if (!(slot instanceof ns.ColorSlot)) {
                slot = new ns.ColorSlot(slot, {
                    parse: true
                });
            }
            this.colors.add(slot);
        },

        addSlots: function (slots) {
            var status = _.map(slots, function (slot) {
                this.addSlot(slot);
            }, this);
            return (status.indexOf(false) === -1);
        },

        addSlot: function (slot) {

            if (!(slot instanceof ns.TimeSlot)) {
                slot = new ns.TimeSlot(slot);
            }

            if (slot.collection && _.isEqual(slot.collection, this)) {
                this.trigger("slotChanged", slot);
                return true;
            }

            if (this.slotCollides(slot.clone().changeDate(this.getDate()))) {
                return false;
            }

            if (slot.get('slots')){
                var self = this;
                _.each(slot.get('slots'), function(collisionslot){
                        collisionslot.changeDate(self.getDate());
                    }
                );
            }

            slot.changeDate(this.getDate());
            var prev;
            if (slot.collection) {
                prev = slot.collection;
                prev.remove(slot);
            }
            this.checkEditable(slot);
            this.add(slot);

            if (prev) {
                prev.trigger("slotRemoved");
            }

            return true;
        },

        getByStart: function (time) {
            return this.find(function (slot) {
                return moment(
                    slot.get("start_time").format("HH:mm"),
                    "HH:mm"
                ).isSame(time);
            });
        },

        timeOccupied: function (time) {
            return !!this.find(function (slot) {
                var start = moment(
                    slot.get("start_time").format("HH:mm"),
                    "HH:mm"
                );
                var end = moment(
                    slot.get("end_time").format("HH:mm"),
                    "HH:mm"
                );
                if (moment().range(start, end).contains(time)) {
                    if (!start.isSame(time) && !end.isSame(time)) {
                        return true;
                    }
                }
                return false;
            });
        },

        getAvailableSpan: function (start) {
            var slots_after = this.filter(function (slot) {
                return (slot.get("start_time").diff(start) > 0);
            });
            if (slots_after.length) {
                var next = _.min(slots_after, function (slot) {
                    return slot.get("start_time").format("X");
                });
                return moment(next.get("start_time"));
            }
            return moment(this.date)
                .hours(this.options.calendar_end.hours())
                .minutes(this.options.calendar_end.minutes())
                .seconds(0);
        },

        destroy: function () {
            this.reset();
            this.trigger("destroy", this);
        }

    });
}(Flod));
var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";


    var EmptySlotView = ns.TimeSlotView.extend({

        events: {
            "click": "clicked"
        },

        className: "slot empty-slot",

        initialize: function () {
            _.bindAll(this, "clicked");
        },

        render: function () {
            this.$el.css('background-color', this.options.background_color);
            return this;
        },

        clicked: function () {
            this.collection.trigger("emptySlotClick", {
                "start_time": this.options.start_time,
                "end_time": this.options.end_time,
                "row": this.collection
            });
        }
    });

    ns.CalendarRowView = Backbone.View.extend({

        tagName: "tr",

        className: "calendar-row",

        initialize: function () {
            _.bindAll(this, "slotDropped");
            this.collection.on("add", this.render, this);
            this.collection.on("remove", this.render, this);
            this.collection.on("slotChanged", this.render, this);
            this.collection.on("slotRemoved", this.render, this);
            this.collection.on("slotRemoved", this.slotRemoved, this);
            this.collection.colors.on("add", this.render, this);
            this.collection.colors.on("remove", this.render, this);
        },

        render: function () {
            this.$el.html($("<td><div class='slot_title' title='" + this.collection.getDisplayName() + "'>" + this.collection.getDisplayName() + "</div></td>"));
            var start = this.collection.options.calendar_start;
            var duration = this.collection.options.slot_duration;
            this.views = _.compact(_.times(this.getNumSlots(), function (index) {
                var slot_start = moment(start).add("minutes", index * duration);
                var slot_end = moment(start).add("minutes", (index + 1) * duration);
                var slot = this.collection.getByStart(slot_start);
                if (slot) {
                    return new ns.TimeSlotView({
                        "model": slot,
                        "slotDuration": duration,
                        "table": this.options.table
                    }).render();
                } else if (!this.collection.timeOccupied(slot_start)) {
                    // Default color is white.
                    var background_color = "#FFFFFF";
                    var colorModel = this.collection.colors.getByTime(slot_start);
                    if (colorModel) {
                        background_color = colorModel.get("background_color");
                    }
                    return new EmptySlotView({
                        "collection": this.collection,
                        "slotDuration": duration,
                        "start_time": slot_start,
                        "end_time": slot_end,
                        "background_color": background_color
                    }).render();
                }
                return null;
            }, this));

            this.$el.append(_.pluck(this.views, "$el"));

            if (this.collection.options.editable) {
                this.$el.droppable({
                    drop: _.bind(function (event, ui) {
                        var offset = (ui.position.left / 28) * 30;
                        var new_start = moment(ui.draggable.data("slot").get("start_time").format("HH:mm"), "HH:mm").add("m", offset);
                        this.slotDropped(ui.draggable.data("slot"), new_start);
                    }, this)
                });
            }
            return this;
        },

        slotDropped: function (slot, time) {

            var diff = time.diff(moment(slot.get("start_time").format("HH:mm"), "HH:mm"), "minutes");

            if (this.collection.canChangeSlotTo(slot, moment(slot.get("start_time")).add(diff, "minutes"), moment(slot.get("end_time")).add(diff, "minutes"))) {
                slot.get("start_time").add(diff, "minutes");
                slot.get("end_time").add(diff, "minutes");
                this.collection.addSlot(slot);
            } else {
                slot.collection.trigger("slotChanged", slot);
            }
        },

        getNumSlots: function () {
            var opts = this.collection.options;
            return opts.calendar_end.diff(opts.calendar_start, "hours") * 60 / opts.slot_duration;
        },

        slotRemoved: function() {
            this.trigger("slotRemoved", this);
        }
    });

}(Flod));
var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    function getNumSlots(start, end, duration) {
        return end.diff(start, "hours") * 60 / duration;
    }

    function addToTr(title, elements, className) {
        var tr = $("<tr><th class='first'>" + title + "</th></tr>");
        tr.append(elements);
        if (className) {
            tr.addClass(className);
        }
        return tr;
    }

    var CalendarHeader = Backbone.View.extend({

        tagName: "thead",

        render: function () {
            var numSlots = getNumSlots(
                this.model.get("calendar_start"),
                this.model.get("calendar_end"),
                this.model.get("slot_duration")
            );
            var start = this.model.get("calendar_start");
            var duration = this.model.get("slot_duration");

            var hours = _.compact(_.times(numSlots, function (index) {
                var slot_start = moment(start).add("minutes", index * duration);
                if (slot_start.minutes() === 0) {
                    return $("<th colspan='2'>" + slot_start.format("H") + "</th>");
                }
            }));
            var minutes = _.compact(_.times(numSlots, function (index) {
                var slot_start = moment(start).add("minutes", index * duration);
                return $("<th>" + slot_start.format("mm") + "</th>");
            }));

            this.$el.append(addToTr(this.model.get("title"), hours));
            this.$el.append(addToTr(this.model.get("subtitle"), minutes, "gray"));

            return this;
        }

    });

    ns.CalendarView = Backbone.View.extend({

        tagName: "table",

        className: "flod-calendar",

        initialize: function () {
            if (!this.model) {
                this.model = new ns.CalendarModel();
            }
            this.model.on("emptySlotClick", this.emptySlotClick, this);
            this.model.on("slotClick", this.slotClick, this);
            this.model.on("reset", this.render, this);
        },

        emptySlotClick: function (e) {
            this.trigger("emptySlotClick", e);
        },

        slotClick: function (e) {
            this.trigger("slotClick", e);
        },

        render: function () {

            if (this.views) {
                _.each(this.views, function (view) {
                    view.undelegateEvents();
                });
            }

            this.header = new CalendarHeader({"model": this.model}).render();

            this.$el.html(this.header.$el);
            this.$el.append($("<tbody></tbody>"));
            this.views = _.map(this.model.get("rows"), function (row) {
                var v = new ns.CalendarRowView({collection: row, "table": this});
                v.on("slotRemoved", this.slotRemoved, this);
                return v.render();
            }, this);
            this.$el.append(_.pluck(this.views, "$el"));
            return this;
        },

        getNumSlots: function () {
            return this.model.get("calendar_end").diff(this.model.get("calendar_start"), "hours") * 60 / this.model.get("slot_duration");
        },

        slotRemoved: function() {
            this.trigger("slotRemoved", this);
        }
    });

}(Flod));
var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var BaseView = Backbone.View.extend({

        editable: true,

        initialize: function () {

            this.calendar = new ns.CalendarModel({
                "rows": [],
                "title": "",
                "subtitle": "",
                "editable": this.editable
            });

            this.calendarView = new Flod.CalendarView({"model": this.calendar});
            this.calendarView.on("emptySlotClick", this.emptySlotClick, this);
            this.calendarView.on("slotClick", this.slotClick, this);
        },

        render: function () {
            this.resetRows();
            this.$el.append(this.calendarView.render().$el);
            return this;
        },

        emptySlotClick: function (data) {
            this.trigger("emptySlotClick", data);
        },

        slotClick: function (data) {
            this.trigger("slotClick", data);
        },

        resetRows: function () {
            this.calendarView.model.reset(
                _.map(this.getDays(this.getInitDate()), function (day) {
                    return {"displayName": day.moment.format("dddd"), "date": day.moment};
                })
            );
        },

        getDays: function (date) {
            var week = new Flod.Week({
                "year": date.year(),
                "week": date.isoWeek()
            });

            return week.getDays();
        }
    });

    var Slots = Backbone.Collection.extend({

        model: ns.TimeSlot,
        type: "slots",

        initialize: function (models, options) {
            this.options = options;
        },

        url: function () {
            var url = "/api/booking/v1/resources" + this.options.resource_uri + "/" + this.type + "/";
            if (this.options.start_date && this.options.end_date) {
                url += "?start_date=" + this.options.start_date + "&end_date=" + this.options.end_date;
            }
            return url;
        }
    });

    var mapSlots = function (res, slot) {
        var date = slot.get("start_time").format("YYYY-MM-DD");
        if (!res[date]) {
            res[date] = [];
        }
        res[date].push(slot);
        return res;
    };


    ns.BrowsableWeeklyCalendarView = BaseView.extend({

        getBlocked: true,

        initialize: function () {
            BaseView.prototype.initialize.apply(this, arguments);
            this.currentWeek = new Flod.Week({
                "year": this.getInitDate().isoWeekYear(),
                "week": this.getInitDate().isoWeek()
            });
            this.weeksChooser = new Flod.WeeksView({"model":  new Flod.Weeks({
                "week": this.currentWeek
            })});
            this.weeksChooser.on("changeWeek", this.changeWeek, this);
            this.rows = [];

            _.bindAll(this, "slotsFectched");
        },

        changeWeek: function (week) {
            var currentRows = _.clone(this.calendarView.model.get("rows"));
            var at = _.find(this.rows, function (row) {
                return row.week.equals(this.currentWeek);
            }, this);
            if (at) {
                at.rows = currentRows;
            } else {
                this.rows.push({"week": this.currentWeek, "rows": currentRows});
            }

            this.currentWeek = week;
            var to = _.find(this.rows, function (row) {
                return row.week.equals(week);
            }, this);
            if (to) {
                this.calendarView.model.reset(to.rows);
            } else {
                this.resetRows();
            }
            this.calendarView.render();
        },

        render: function () {
            BaseView.prototype.render.apply(this, arguments);
            this.$el.append(this.weeksChooser.render().$el);
            this.$el.append(this.calendarView.render().$el);
            return this;
        },

        getInitDate: function () {
            return moment(this.options.data.date);
        },

        resetRows: function () {
            var days = this.currentWeek.getDays();
            this.trigger("resetRows", days);

            var slots = new Slots([], {
                "resource_uri": this.options.data.resource.get("uri"),
                "start_date": days[0].moment.format("YYYY-MM-DD"),
                "end_date": days[days.length - 1].moment.format("YYYY-MM-DD")
            });


            if (this.getBlocked) {
                var blocked = new Slots([], {
                    "resource_uri": this.options.data.resource.get("uri"),
                    "start_date": days[0].moment.format("YYYY-MM-DD"),
                    "end_date": days[days.length - 1].moment.format("YYYY-MM-DD")
                });
                blocked.type = "blockedtimes";
                var showSlots = _.after(2, _.bind(function () {
                    this.slotsFectched(slots, blocked);
                }, this));

                slots.fetch({"success": showSlots});
                blocked.fetch({"success": showSlots});
            } else {
                slots.fetch({"success": _.bind(function () {
                    this.slotsFectched(slots);
                }, this)});
            }
        },

        slotsFectched: function (slots, blocked) {
            var mappedSlots = slots.reduce(mapSlots, {});


            if (blocked) {
                blocked.each(function (slot) {
                    slot.set("status", "reserved");
                });

                var mappedBlocked = blocked.reduce(mapSlots, {});

                _.each(mappedBlocked, function (value, key) {
                    if (_.has(mappedSlots, key)) {
                        mappedSlots[key] = mappedSlots[key].concat(value);
                    } else {
                        mappedSlots[key] = value;
                    }
                });
            }

            _.each(mappedSlots, function (slots, date) {
                var row = _.find(this.calendar.get("rows"), function (row) {
                    return row.date.isSame(moment(date), "day");
                });

                slots = _.filter(slots, function (slot) {
                    return (slot.getStatus() === "granted" || slot.getStatus() === "reserved");
                });

                _.each(slots, function (slot) {
                    slot.set("editable", false);
                });
                row.addSlots(slots);
            }, this);
        }
    });

    ns.IdealizedWeeklyCalendarView = BaseView.extend({
        getInitDate: function () {
            return moment();
        }
    });

}(Flod));

var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    function isoWeeksInYear(year) {
        function weekOfYear(mom, firstDayOfWeek, firstDayOfWeekOfYear) {
            var end = firstDayOfWeekOfYear - firstDayOfWeek,
                daysToDayOfWeek = firstDayOfWeekOfYear - mom.day(),
                adjustedMoment;
            if (daysToDayOfWeek > end) {
                daysToDayOfWeek -= 7;
            }
            if (daysToDayOfWeek < end - 7) {
                daysToDayOfWeek += 7;
            }
            adjustedMoment = moment(mom).add(daysToDayOfWeek, 'd');
            return {
                week: Math.ceil(adjustedMoment.dayOfYear() / 7),
                year: adjustedMoment.year()
            };
        }

        function weeksInYear(year, dow, doy) {
            return weekOfYear(moment([year, 11, 31 + dow - doy]), dow, doy).week;
        }

        return weeksInYear(year, 1, 4);
    }


    ns.Week = Backbone.Model.extend({

        weekDayFormat: "dddd",
        dayFormat: "D.M",

        _getLastValidDay: function () {
            var firstDayOfYear = moment(this.get("year") + "-01-04", "YYYY-MM-DD"); // The Jan 4th must be in week 1 according to ISO
            firstDayOfYear.endOf("isoWeek");
            firstDayOfYear.add("w", parseInt(this.get("week"), 10) - 1);
            return firstDayOfYear;
        },

        _changeWeek: function (offset) {
            var numWeeks = isoWeeksInYear(this.get('year'));
            var current = this.get('week');
            var changedWeek = current + offset;

            var year = this.get('year');
            if (changedWeek < 1) {
                year = year - 1;
                changedWeek = isoWeeksInYear(year)+changedWeek;
            } else if (changedWeek > numWeeks) {
                year = year + 1;
                changedWeek = changedWeek - numWeeks;
            }
            this.set({
                "year": year,
                "week": changedWeek
            });
        },

        _asRange: function () {
            return moment().range(this.getFirstValidDay(), this._getLastValidDay());
        },

        getFirstValidDay: function () {
            var firstDayOfYear = moment(this.get("year") + "-01-04", "YYYY-MM-DD"); // The Jan 4th must be in week 1 according to ISO
            firstDayOfYear.startOf("isoWeek");
            firstDayOfYear.add("w", parseInt(this.get("week"), 10) - 1);
            return firstDayOfYear;
        },

        getDisplayStr: function () {
            return "Uke " + this.get("week") + ", " + this.get("year");
        },

        getDays: function () {
            var firstDay = this.getFirstValidDay();
            var lastDay = this._getLastValidDay();
            var diff = lastDay.diff(firstDay, "days");

            return _.map(_.range(0, diff + 1), function (offset) {
                var date = moment(firstDay).add("d", offset);
                return {
                    "moment": date
                };
            });
        },

        hasPrev: function () {
            if (!this.has("range")) {
                return true;
            }
            return !this._asRange().contains(this.get("range").start);

        },

        hasNext: function () {
            if (!this.has("range")) {
                return true;
            }
            return !this._asRange().contains(this.get("range").end);
        },

        next: function () {
            if (this.hasNext()) {
                this._changeWeek(1);
            }
            return this;
        },

        prev: function () {
            if (this.hasPrev()) {
                this._changeWeek(-1);
            }
            return this;
        },

        nextMonth: function () {
            if (this.hasNext()) {

                var nextWeek = this.get("week") + 4;

                if (this.has("range")) {
                    var rangeEnd = moment(this.get("range").end).isoWeek();
                    if (nextWeek > rangeEnd){
                        nextWeek = rangeEnd;
                    }
                }

                nextWeek -= this.get("week");

                this._changeWeek(nextWeek);
            }
            return this;
        },

        prevMonth: function () {
            if (this.hasPrev()) {
                var nextWeek = this.get("week") - 4;

                if (this.has("range")) {
                    var rangeEnd = moment(this.get("range").start).isoWeek();
                    if (nextWeek < rangeEnd){
                        nextWeek = rangeEnd;
                    }
                }

                nextWeek -= this.get("week");

                this._changeWeek(nextWeek);
            }
            return this;
        },

        equals: function (week) {
            return (this.get("week") === week.get("week") && this.get("year") === week.get("year"));
        }
    });

}(Flod));




var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    moment.lang('no', {
        months : [
            "Januar", "Februar", "Mars", "April", "Mai", "Juni", "Juli",
            "August", "September", "Oktober", "November", "Desember"
        ],
        weekdays : [
            "Søndag", "Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag"
        ],
        weekdaysShort : ["S", "M", "T", "O", "T", "F", "L"]
    });

    moment.lang("no");


    var ElementView = Backbone.View.extend({

        tagName: "td",

        className: "selectable",

        events: {
            "click": "change"
        },

        initialize: function () {
            _.bindAll(this, "change");
        },

        render: function () {
            if (this.model.get("selected")) {
                this.$el.addClass("selected current");
            } else {
                this.$el.addClass("otherdate");
            }
            if (this.model.get("disabled")) {
                this.$el.addClass("disabled");
            }
        }
    });

    var DayView = ElementView.extend({


        template: "<div><%= day_name %></div><div><%= date %></div>",

        render: function () {
            ElementView.prototype.render.apply(this, arguments);
            this.$el.html(_.template(this.template, {
                "day_name": this.model.get("moment").format(this.model.get("weekDayFormat")),
                "date": this.model.get("moment").format(this.model.get("dayFormat"))
            }));
            return this;
        },

        change: function () {
            if (!this.model.get("disabled")) {
                this.options.parent.change(this.model.get("moment"));
            }
        }
    });


    var ChooserView = Backbone.View.extend({

        tagName: "table",

        className: "flod-calendar flod-calendar-chooser",

        template: '<tr><td><%= title %></td></tr>',

        render: function () {
            this.$el.html(_.template(this.template, {"title": this.model.getDisplayStr()}));
            if (this.model.hasPrev()) {
                var prevMonth = $('<td class="flod-btn"><i><img src="/static/images/backward2.png" height="26" width="17"></i></td>');
                this.$("tr").append(prevMonth);
                prevMonth.on("click", _.bind(this.prevMonth, this));

                var prevBtn = $('<td class="flod-btn"><i id="left"><img src="/static/images/backward1.png" height="26" width="17"></i></td>');
                this.$("tr").append(prevBtn);
                prevBtn.on("click", _.bind(this.prev, this));
            }

            this.renderElements();

            if (this.model.hasNext()){
                var nextBtn = $('<td class="flod-btn right"><i id="right"><img src="/static/images/forward1.png" height="26" width="17"></i></td>');
                this.$("tr").append(nextBtn);
                nextBtn.on("click", _.bind(this.next, this));

                var nextMonth = $('<td class="flod-btn"><i><img src="/static/images/forward2.png" height="26" width="17"></i></td>');
                this.$("tr").append(nextMonth);
                nextMonth.on("click", _.bind(this.nextMonth, this));
            }

            return this;
        },

        prev: function () {

        },

        prevMonth: function () {

        },

        next: function () {

        },

        nextMonth: function () {

        }
    });

    ns.WeekView = ChooserView.extend({

        renderElements: function () {
            var range;
            if (this.model.has("range")) {
                range = moment().range(moment(this.model.get("range").start.format("YYYY-MM-DD"), "YYYY-MM-DD"), moment(this.model.get("range").end.format("YYYY-MM-DD"), "YYYY-MM-DD"));
            }
            var days = _.map(this.model.getDays(), function (day) {
                day.weekDayFormat = this.model.weekDayFormat;
                day.dayFormat = this.model.dayFormat;
                if (this.options.selected) {
                    day.selected = this.options.selected.isSame(day.moment, "day");
                }
                if (range) {
                    day.disabled = !range.contains(day.moment);
                }
                return new DayView({"model": new Backbone.Model(day), "parent": this}).render().$el;
            }, this);
            this.$("tr").append(days);
        },

        change: function (day) {
            this.options.selected = day;
            this.trigger("changeDay", day);
            this.render();
        },

        prev: function () {
            if (this.model.hasPrev()) {
                this.model.prev();
                var d = moment(this.options.selected).subtract(7, "days").endOf("isoWeek");
                this.change(d);
            }
        },

        prevMonth: function () {
            if (this.model.hasPrev()) {
                this.model.prevMonth();
                var d = moment(this.options.selected).subtract(4, "w").endOf("isoWeek");
                if (this.model.has("range")) {
                    var rangeEnd = moment(this.model.get("range").start).endOf("isoWeek");
                    if (rangeEnd > d){
                        d = rangeEnd
                    }
                }
                this.change(d);
            }
        },

        next: function () {
            if (this.model.hasNext()) {
                this.model.next();
                var d = moment(this.options.selected).add(7, "days").startOf("isoWeek");
                this.change(d);
            }
        },

        nextMonth: function () {
            if (this.model.hasNext()) {
                this.model.nextMonth();
                var d = moment(this.options.selected).add(4, "w").startOf("isoWeek");
                if (this.model.has("range")) {
                    var rangeEnd = moment(this.model.get("range").end).startOf("isoWeek");
                    if (rangeEnd < d){
                        d = rangeEnd
                    }
                }
                this.change(d);
            }
        }
    });

    var WeekElementView = ElementView.extend({
        render: function () {
            ElementView.prototype.render.apply(this, arguments);
            this.$el.html("Uke " + this.model.get("week"));
            return this;
        },

        change: function () {
            this.options.parent.change(this.model);
        }
    });

    ns.WeeksView = ChooserView.extend({

        renderElements: function () {
            var weeks = _.map(this.model.getWeeks(), function (week) {
                week.set("selected", false);
                if (week.equals(this.model.get("week"))) {
                    week.set("selected", true);
                }
                return new WeekElementView({"model": week, "parent": this}).render().$el;
            }, this);
            this.$("tr").append(weeks);
        },

        change: function (week) {
            this.model.set("week", week);
            this.trigger("changeWeek", week);
            this.render();
        },

        prev: function () {
            this.change(this.model.prev());
        },

        next: function () {
            this.change(this.model.next());
        },

        prevMonth: function () {
            this.change(this.model.prevMonth());
        },

        nextMonth: function () {
            this.change(this.model.nextMonth());
        }
    });

}(Flod));
var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";
    ns.Weeks = Backbone.Model.extend({

        getDisplayStr: function () {
            return "Uke " + this.get("week").get("week") + ", " + this.get("week").get("year");
        },

        getWeeks: function () {
            return [
                this.get("week").clone().prev(),
                this.get("week").clone(),
                this.get("week").clone().next()
            ];
        },

        next: function () {
            return this.get("week").clone().next();
        },

        nextMonth: function () {
            return this.get("week").clone().nextMonth();
        },

        prev: function () {
            return this.get("week").clone().prev();
        },

        prevMonth: function () {
            return this.get("week").clone().prevMonth();
        },

        hasPrev: function () {
            return true;
        },

        hasNext: function () {
            return true;
        }
    });
}(Flod));
$.widget("ui.draggable", $.extend({}, $.ui.draggable.prototype, {
    _setContainment: function () {
        "use strict";
        var over, c, ce,
            o = this.options;

        c = $(o.containment);
        ce = c[0];

        if (!ce) {
            return;
        }

        over = c.css("overflow") !== "hidden";

        var offset_left = c.children().first().children().first().width();

        this.containment = [
            (parseInt(c.css("borderLeftWidth"), 10) || 0) + (parseInt(c.css("paddingLeft"), 10) || 0) + offset_left,
            (parseInt(c.css("borderTopWidth"), 10) || 0) + (parseInt(c.css("paddingTop"), 10) || 0),
            (over ? Math.max(ce.scrollWidth, ce.offsetWidth) : ce.offsetWidth) - (parseInt(c.css("borderRightWidth"), 10) || 0) - (parseInt(c.css("paddingRight"), 10) || 0) - this.helperProportions.width - this.margins.left - this.margins.right,
            (over ? Math.max(ce.scrollHeight, ce.offsetHeight) : ce.offsetHeight) - (parseInt(c.css("borderBottomWidth"), 10) || 0) - (parseInt(c.css("paddingBottom"), 10) || 0) - this.helperProportions.height - this.margins.top  - this.margins.bottom
        ];
        this.relative_container = c;
    }
}));
var Flod = window.Flod || {};
Flod.calendar = Flod.calendar || {};

(function (ns, undefined) {
    "use strict";

    function createSlot(start_time, end_time, week_day) {
        return new Flod.TimeSlot({
            "start_time": start_time,
            "end_time": end_time,
            "week_day": week_day,
            "editable": false,
            "status": "reserved"
        });
    }

    function invertDay(day, slots) {

        slots = _.sortBy(slots, function (slot) {
            return slot.get('start_time').unix();
        });

        var test = _.map(slots, function (slot) {
            return [slot.get("start_time"), slot.get("end_time")];
        });

        test.unshift([moment("08:00", "HH:mm"), moment("08:00", "HH:mm")]);
        test.push([moment("23:00", "HH:mm"), moment("23:00", "HH:mm")]);

        return _.compact(_.map(test, function (span1, index, array) {
            if (array[index + 1]) {
                var span2 = array[index + 1];
                var start = span1[1];
                var end = span2[0];
                if (start.diff(end) !== 0) {
                    return createSlot(start, end, day);
                }
            }
        }));
    }

    /*
        input: a dict with the following structure
        {
            week_day: [slot, ..],
            week_day2: [slot, ..]
        }
        where week_day is an int (isoweekday) and slot is a TimeSlot

        returns a similar structure, but "inverted", i.e the slots are now free, and the free slots are filled
     */
    ns.invertSlots = function (slotDict) {

        return _.reduce(_.range(1, 8), function (res, day) {
            res[day] = invertDay(day, slotDict[day]);
            return res;
        }, {});
    };

    var subtract = function (source, target) {
        var clone = source.clone();

        var sameStart = clone.get('start_time').isSame(target.get('start_time'));
        var sameEnd = clone.get('end_time').isSame(target.get('end_time'));

        if (sameStart && sameEnd) {
            return null;
        }
        if (sameStart) {
            clone.set('start_time', moment(target.get('end_time')));
            return [clone];
        }
        if (sameEnd) {
            clone.set('end_time', moment(target.get('start_time')));
            return [clone];
        }
        if (clone.get('start_time').isBefore(target.get('start_time')) && clone.get('end_time').isAfter(target.get('end_time'))) {

            var clone2 = clone.clone();
            clone.set('end_time', target.get('start_time'));
            clone2.set('start_time', target.get('end_time'));
            return [clone, clone2];
        }
        if (target.get('start_time').isBefore(clone.get('start_time'))) {
            clone.set('start_time', target.get('end_time'));
            return [clone];
        }

        if (target.get('end_time').isAfter(clone.get('end_time'))) {
            clone.set('end_time', target.get('start_time'));
            return [clone];
        }

        return [source];
    };

    function compare(a, b) {
        if (a.get('start_time').unix() < b.get('start_time').unix()) {
            return -1;
        }
        if (a.get('start_time').unix() > b.get('start_time').unix()) {
            return 1;
        }
        return 0;
    }

    ns.splitSlot = function (toSplit, splitWith) {
        splitWith.sort(compare);
        var check = [toSplit];
        _.each(splitWith, function (split) {
            var target = check.shift();
            if (target.collidesWith(split)) {
                var res = subtract(target, split);
                _.each(res, function (r) {
                    check.unshift(r);
                });
            } else {
                check.unshift(target);
            }
        });
        return _.compact(check).reverse();
    };

}(Flod.calendar));