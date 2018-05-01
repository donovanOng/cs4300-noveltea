var use_features = false;

$('.collapse').on('show.bs.collapse', function () {
    var $this = $(this);
    if ($this.attr('data-href')) {
        document.getElementById("collapse" + $this.attr('data-href')).innerHTML =
            "<div class=\"card card-body p-3\">Loading...</div>";

        $.getJSON("getRelatedTeas/?tea_id=" + $this.attr('data-href'), function (teas) {
            if (teas.length == 0) {
                var teaString = "<div class=\"card card-body p-3 bg-light\">"
                teaString +=
                    "<p class=\"mb-0 font-weight-bold\" style=\"font-size:0.8rem\">Sorry! No similar teas found.</p>";
            } else {
                var teaString =
                    "<div class=\"card card-body p-3 bg-light\"><p class=\"mb-2 font-weight-bold\">Similar Teas:</p>";
                teas.forEach(function (tea) {
                    tea = JSON.parse(tea)
                    teaString += "<li><a href=\"" + tea.url + "\">" + tea.name +
                        "</a> by " + tea.brand + "</li>"
                })
            }
            document.getElementById("collapse" + $this.attr('data-href')).innerHTML = teaString +
                "</div>";
        });
    }
})

function checkSubmit(filterType) {
    var filterList = $('.' + filterType + 'CB:not(:checked)').map(function () {
        return this.value;
    }).get().join(',');
    if (filterList) {
        $("#" + filterType + "Filter").val(filterList);
    } else {
        $("#" + filterType + "Filter").remove();
    }
    $("#" + filterType + 'Form').submit();
}

// Co_occurence matrix used
var flavs = $("#search_input").tagsinput('items').itemsArray;
var flavor_to_index, index_to_flavor, cooc;

var to_index_file = use_features ? "/static/data/features_to_index.json" : "/static/data/flavor_to_index.json"
$.getJSON(to_index_file, function (json) {
    flavor_to_index = json;

    $("input")
    // don't navigate away from the field on tab when selecting an item
    .on("keydown", function (event) {
        if (event.keyCode === $.ui.keyCode.TAB &&
            $(this).autocomplete("instance").menu.active) {
            event.preventDefault();
        }
    })
    .autocomplete({
        source: Object.keys(flavor_to_index).map(x => x.toLowerCase()),
        search: function () {
            // custom minLength
            var term = extractLast(this.value);
            if (term.length < 2) {
                return false;
            }
        },
        focus: function () {
            // prevent value inserted on focus
            return false;
        },
        select: function (event, ui) {
            var terms = split(this.value);
            // remove the current input
            terms.pop();
            addFlavorToInput(ui.item.value)
            this.value = ""

            return false;
        }
    });
});

var index_to_file = use_features ? "/static/data/index_to_features.json" : "/static/data/index_to_flavor.json"
$.getJSON(index_to_file, function (json) {
    index_to_flavor = json;
});


//CHANGE
var co_oc_file = use_features ? "/static/data/co_oc_features.txt" : "/static/data/co_oc.txt"
$.get(co_oc_file, function (csv) {
    cooc = csv;
    cooc = cooc.trim();
    cooc = JSON.parse(cooc);
});

function showComplements() {
    if (flavs && flavs.length > 0 && flavs.length <= 3) {
        var suggested = getComplements(flavs, 5);
        var suggestString = ""
        suggested.forEach(function (d) {
            suggestString += "<a href='#' onclick='addFlavorToInput(\"" + d + "\")' class='ml-2'>" + d +
                "</a>";
        })
        document.getElementById("suggest").innerHTML =
            '<span class="font-italic font-weight-light">You might also like</span>' + suggestString;
    } else {
        document.getElementById("suggest").innerHTML = "";
    }
}

function addFlavorToInput(flavor) {
    $('#search_input').tagsinput('add', flavor);
    showComplements();
}

function getComplements(flavors_query, topx) {
    sum_flavors = new Array(358 + 1).join('0').split('').map(parseFloat);

    flavors_query.forEach(function (d) {
        sum_flavors = sum_flavors.map(function (num, idx) {
            return num + cooc[flavor_to_index[title(d)]][idx];
        });
    })

    flavors_query.forEach(function (d) {
        sum_flavors[flavor_to_index[title(d)]] = 0;
    })

    var topflavorsIndices = findIndicesOfMax(sum_flavors, topx);
    var topflavors = [];

    topflavorsIndices.forEach(function (d) {
        if (sum_flavors[d] > 0) {
            topflavors.push(index_to_flavor[d]);
        }
    })
    return topflavors;
}

function title(s) {
    words = s.split(" ")
    result = ""

    words.forEach(function (d) {
        result += d[0].toUpperCase() + d.slice(1).toLowerCase() + " "
    })

    return result.trim()
}

function findIndicesOfMax(inp, count) {
    // Src: https://stackoverflow.com/questions/11792158/optimized-javascript-code-to-find-3-largest-element-and-its-indexes-in-array
    var outp = [];
    for (var i = 0; i < inp.length; i++) {
        outp.push(i); // add index to output array
        if (outp.length > count) {
            outp.sort(function (a, b) {
                return inp[b] - inp[a];
            }); // descending sort the output array
            outp.pop(); // remove the last index (index of smallest element in output array)
        }
    }
    return outp;
}

function split(val) {
    return val.split(/,\s*/);
}

function extractLast(term) {
    return split(term).pop();
}

$('input').on('beforeItemAdd', function(event) {
    var flavors = Object.keys(flavor_to_index).map(x => x.toLowerCase())
    if (flavors.indexOf(event.item) < 0) {
        event.cancel = true
    }
});

// Src: http://jsfiddle.net/iambriansreed/bjdSF/
var minimized_elements = $('span.minimize');

minimized_elements.each(function() {
    var MAX_CHARS = 150;
    var t = $(this).text();
    if(t.length < MAX_CHARS) return;

    $(this).html(
        t.slice(0,MAX_CHARS)+'<span>... </span><a href="#" class="more">More</a>'+
        '<span style="display:none;">'+ t.slice(MAX_CHARS,t.length)+' <a href="#" class="less">Less</a></span>'
    );

});

$('a.more', minimized_elements).click(function(event){
    event.preventDefault();
    $(this).hide().prev().hide();
    $(this).next().show();
});

$('a.less', minimized_elements).click(function(event){
    event.preventDefault();
    $(this).parent().hide().prev().show().prev().show();
});
