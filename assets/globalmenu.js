$.getJSON("https://res.de.dariah.eu/globalmenu/menu.json", function( data ) {

var ul_main = $("<ul id='home_dropdown_menu' class='nav_list -level-2 -portal'></ul>");

$.each(data['menu'], function (key, val) {
	if (typeof val.title !== "undefined") {
		var li = $("<li class='nav_item -level-2'>",  { id: 'li' + key, text : val.title });
		var a = $("<a class='nav_link' href='" + val.link + "'>" + val.title + "</a></li>");

		a.appendTo(li);

    if (val.submenu != null) {

        var ul = $("<ul>", { class: 'nav_list -level-3' });

        $.each(val.submenu, function (key, sub) {
        	if (sub.title) {
            ul.append("<li class='nav_item -level-3'><a class='nav_link' href='" + sub.link + "'>" + sub.title + "</a></li>")
            }
           else {
            ul.append("<li class='nav_item -level-3'><hr></li>")
           }

        });

        ul.appendTo(li);
    }
    li.appendTo(ul_main);
}});

$( 'ul#home_dropdown_menu' ).replaceWith(ul_main);

}).fail(function() {
  console.log( 'Error loading menu JSON!' );
});
