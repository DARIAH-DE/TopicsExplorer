// load global menu JSON and re-populate the global navigation menu
// Copyright 2016 SUB Göttingen
// Author Carsten Thiel
//
$.getJSON( 'https://res.de.dariah.eu/globalmenu/menu.json', function( data ) {

  // replace the existing menu with an empty one
  $( 'ul#home_dropdown_menu' ).replaceWith( '<ul id="home_dropdown_menu" class="dropdown-menu"></ul>' );

  var liFromArrayItem = function (arrayItem) {
    // create an empty li
    var myObject = document.createElement('li');
    var linkTarget, tabIndexString, classString;
    if ('divider' in arrayItem) {
      // make it a divider
      $(myObject).addClass('divider');
    } else {
      // check whether there is a link and not a submenu
      if ('link' in arrayItem && !('submenu' in arrayItem)) {
        linkTarget = arrayItem['link'];
        tabIndexString = '';
        classString = 'class="navtarget"';
      } else {
        linkTarget = '#';
        tabIndexString = 'tabindex="-1"';
        classString = '';
      }
      // add the link inside
      $(myObject).html('<a '+ tabIndexString +' href="' + linkTarget + '" '+classString+'>' + arrayItem['title'] + '</a>');
      // if the li has a submenu, add another ul
      if ('submenu' in arrayItem) {
        $(myObject).addClass('dropdown-submenu');
        var newsubmenu = document.createElement('ul');
        $(newsubmenu).addClass('dropdown-menu');
        // for each cild, recurse!
        $.each(arrayItem['submenu'], function (arrayId, arrayItem) {
          $(newsubmenu).append(liFromArrayItem(arrayItem));
        });
        $(myObject).append(newsubmenu);
      }
    }
    return myObject;
  };

  // loop through the outer array and append childs to the new ul from above
  $.each( data['menu'], function( arrayId, arrayItem ) {
    $( 'ul#home_dropdown_menu' ).append( liFromArrayItem(arrayItem) );
  });

}).fail(function() {
  console.log( 'Error loading menu JSON!' );
});


// submenu workaround for mobiles.
$(function() {
  $('.navbar-dariah').on('touchstart click tap', 'li.dropdown-submenu > a', function(e) {
    e.preventDefault(); // do not aktivate links
    e.stopPropagation(); // do not propagate event to top eventHandlers
	
	//close other submenus
    $('li.dropdown-submenu').each(function( index ){
    	$(this).removeClass('open');
    });
	
    $(this).parent('li').toggleClass('open');
  });

  $('.navbar-dariah').on('touchstart click tap', 'a.navtarget', function(e) {
    e.stopPropagation(); // do not propagate event to top eventHandlers
  });
});

