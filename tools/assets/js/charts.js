;(function () {
    let generateChartTimeout = null;
    window.addEventListener('resize', function () {
        clearTimeout(generateChartTimeout);
        generateChartTimeout = setTimeout(function () {
            generateD3Charts();
        }, 200);
    });
    generateD3Charts();

    var inter = setInterval(function() {
        generateD3Charts();
    }, 5000); 

    function generateD3Charts () {
        const columnWidth = document.querySelector('.columns :first-child').clientWidth;

        // Set the dimensions of the canvas
        const margin = { top: 20, right: 20, bottom: 70, left: 40 },
            width = columnWidth - margin.left - margin.right,
            height = Math.max(width / 3, 250) - margin.top - margin.bottom;

        // Set the ranges
        const x = d3.scale.ordinal().rangeRoundBands([0, width], .05);
        const y = d3.scale.linear().range([height, 0]);

        // Define the axis
        const xAxis = d3.svg.axis()
                            .scale(x)
                            .orient('bottom');

        const yAxis = d3.svg.axis()
                            .scale(y)
                            .orient('left')
                            .ticks(10);

        // Define the div for the tooltip
        const div = d3.select('body').append('div')
                      .attr('class', 'tooltip')
                      .style('opacity', 0);

        // Activity
        // Load the data
        d3.json('activity.json', function (error, data) {
            const containerSelector = '.activity-graph';
            const containerTitle = 'Activité heure par heure';

            d3.select(containerSelector).html('');
            data.forEach(function(d) {
                d.Hour = d.Hour;
                d.TX = d.TX;
            });

            // Scale the range of the data
            x.domain(data.map(function(d) { return d.Hour; }));
            y.domain([0, d3.max(data, function(d) { return d.TX; })]);

            var svg_activity = d3.select(containerSelector)
                                 .append('svg')
                                 .attr('width', width + margin.left + margin.right)
                                 .attr('height', height + margin.top + margin.bottom)
                                 .append('g')
                                 .attr('transform',
                                       'translate(' + margin.left + ',' + margin.top + ')');

            // Add axis
            svg_activity.append('g')
                        .attr('class', 'x axis')
                        .attr('transform', 'translate(0,' + (height + 0.5) + ')')
                        .call(xAxis)
                        .selectAll('text')
                        .style('text-anchor', 'end')
                        .attr('dx', '-.8em')
                        .attr('dy', '-.55em')
                        .attr('transform', 'rotate(-45)' );

            svg_activity.append('g')
                        .attr('class', 'y axis')
                        .call(yAxis)
                        .append('text')
                        .attr('transform', 'rotate(0)')
                        .attr('y', -10)
                        .attr('dy', '.71em')
                        .style('text-anchor', 'end')
                        .text('TX');

            svg_activity.append('text')
                        .attr('x', (width / 2))
                        .attr('y', 0 - (margin.top / 3))
                        .attr('text-anchor', 'middle')
                        .style('font-size', '16px')
                        .style('font-family', 'Arial')
                        .text(containerTitle);

            // Add bar chart
            svg_activity.selectAll('bar')
                        .data(data)
                        .enter().append('rect')
                        .attr('class', 'bar')
                        .attr('x', function(d) { return x(d.Hour); })
                        .attr('width', x.rangeBand())
                        .attr('y', function(d) { return y(d.TX); })
                        .attr('height', function(d) { return height - y(d.TX); })
                        .on('mouseover', function(d) {
                            div.transition()
                            .duration(200)
                            .style('opacity', .9);

                            div.html(d.TX)
                            .style('left', (d3.event.pageX) + 'px')
                            .style('top', (d3.event.pageY) + 'px');
                        })
                        .on('mouseout', function(d) {
                            div.transition()
                            .duration(500)
                            .style('opacity', 0);
                        })
        });

        // Best
        // Load the data
        d3.json('best.json', function (error, data) {
            const containerSelector = '.best-graph';
            const containerTitle = 'Top 20 des noeuds les plus actifs';

            d3.select(containerSelector).html('');

            data.forEach(function (d) {
                d.Call = d.Call;
                d.TX = d.TX;
            });

            const svg_best = d3.select(containerSelector)
                               .append('svg')
                               .attr('width', width + margin.left + margin.right)
                               .attr('height', height + margin.top + margin.bottom)
                               .append('g')
                               .attr('transform',
                                     'translate(' + margin.left + ',' + margin.top + ')');

            // Scale the range of the data
            x.domain(data.map(function(d) { return d.Call; }));
            y.domain([0, d3.max(data, function(d) { return d.TX; })]);

            // Add axis
            svg_best.append('g')
                    .attr('class', 'x axis')
                    .attr('transform', 'translate(0,' + (height + 0.5) + ')')
                    .call(xAxis)
                    .selectAll('text')
                    .style('text-anchor', 'end')
                    .attr('dx', '-.8em')
                    .attr('dy', '-.55em')
                    .attr('transform', 'rotate(-45)' );

            svg_best.append('g')
                    .attr('class', 'y axis')
                    .call(yAxis)
                    .append('text')
                    .attr('transform', 'rotate(0)')
                    .attr('y', -10)
                    .attr('dy', '.71em')
                    .style('text-anchor', 'end')
                    .text('TX');

            svg_best.append('text')
                    .attr('x', (width / 2))
                    .attr('y', 0 - (margin.top / 3))
                    .attr('text-anchor', 'middle')
                    .style('font-size', '16px')
                    .style('font-family', 'Arial')
                    .text(containerTitle);

            // Add bar chart
            svg_best.selectAll('bar')
                    .data(data)
                    .enter().append('rect')
                    .attr('class', 'bar')
                    .attr('x', function(d) { return x(d.Call); })
                    .attr('width', x.rangeBand())
                    .attr('y', function(d) { return y(d.TX); })
                    .attr('height', function(d) { return height - y(d.TX); })
                    .on('mouseover', function(d) {
                        div.transition()
                           .duration(200)
                           .style('opacity', .9);
                        div.html(d.Call + '<br/>' + d.TX)
                           .style('left', (d3.event.pageX) + 'px')
                           .style('top', (d3.event.pageY) + 'px');
                    })
                    .on('mouseout', function(d) {
                        div.transition()
                        .duration(500)
                        .style('opacity', 0);
                    });
        });

        // Abstract
        // Load the data
        d3.json('abstract.json', function(error, data) {
            const containerSelector = '.abstract-graph';
            const containerTitle = 'Résumé de la journée';

            function tabulate (data, columns) {
                d3.select(containerSelector).html('');
                d3.select(containerSelector).append('h2').text(containerTitle);

                const table = d3.select(containerSelector).append('table');
                const thead = table.append('thead');
                const tbody = table.append('tbody');

                // Append the header row
                thead.append('tr')
                    .selectAll('th')
                    .data(columns).enter()
                    .append('th')
                    .text(function (column) { return column; });

                // Create a row for each object in the data
                const rows = tbody.selectAll('tr')
                                .data(data)
                                .enter()
                                .append('tr');

                // Create a cell in each row for each column
                const cells = rows.selectAll('td')
                                .data(function (row) {
                                    return columns.map(function (column) {
                                        return {column: column, value: row[column]};
                                    });
                                })
                                .enter()
                                .append('td')
                                .text(function (d) { return d.value; });

                return table;
            }

            // Render the table(s)
            tabulate(data, ['Salon', 'Date', 'TX total', 'Noeuds actifs']); // 3 columns table
        });

        // Last
        // Load the data
        d3.json('last.json', function (error, data) {
            const containerSelector = '.last-graph';
            const containerTitle = 'Derniers passages en émission';

            function tabulate (data, columns) {
                d3.select(containerSelector).html('');
                d3.select(containerSelector).append('h2').text(containerTitle);


                var table = d3.select(containerSelector).append('table');
                var thead = table.append('thead');
                var tbody = table.append('tbody');

                // Append the header row
                thead.append('tr')
                    .selectAll('th')
                    .data(columns).enter()
                    .append('th')
                    .text(function (column) { return column; });

                // Create a row for each object in the data
                var rows = tbody.selectAll('tr')
                                .data(data)
                                .enter()
                                .append('tr');

                // Create a cell in each row for each column
                var cells = rows.selectAll('td')
                                .data(function (row) {
                                    return columns.map(function (column) {
                                        return { column: column, value: row[column] };
                                    });
                                })
                                .enter()
                                .append('td')
                                .text(function (d) { return d.value; });

                return table;
            }

            // Render the table(s)
            tabulate(data, ['Date', 'Call']); // 2 columns table
        });

        // All
        // Load the data
        d3.json('all.json', function (error, data) {
            const containerSelector = '.all-graph';
            const containerTitle = 'Classement des noeuds actifs';

            function tabulate (data, columns) {
                d3.select(containerSelector).html('');
                d3.select(containerSelector).append('h2').text(containerTitle);


                var table = d3.select(containerSelector).append('table');
                var thead = table.append('thead');
                var tbody = table.append('tbody');

                // Append the header row
                thead.append('tr')
                    .selectAll('th')
                    .data(columns).enter()
                    .append('th')
                    .text(function (column) { return column; });

                // Create a row for each object in the data
                var rows = tbody.selectAll('tr')
                                .data(data)
                                .enter()
                                .append('tr');

                // Create a cell in each row for each column
                var cells = rows.selectAll('td')
                                .data(function (row) {
                                    return columns.map(function (column) {
                                        return { column: column, value: row[column] };
                                    });
                                })
                                .enter()
                                .append('td')
                                .text(function (d) { return d.value; });

                return table;
            }

            // Render the table(s)
            tabulate(data, ['Pos', 'Call', 'TX']); // 3 columns table
        });
    }
})();