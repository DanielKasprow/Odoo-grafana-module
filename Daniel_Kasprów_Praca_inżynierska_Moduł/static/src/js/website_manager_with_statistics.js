/** @odoo-module **/
    var rpc = require('web.rpc');

    //Zmienna z wyświetlaniem wykresu
    var chart = document.getElementById('chart');

    //zmniennie związane z przyciskami radio button
    var radioButtonTimeSpan = document.getElementById('fieldTimeSpan');
    var radioButtonTypeOfReport = document.getElementById('fieldTypeOfReport');
    var radioButtonFieldSelectDataToAnalyze = document.getElementById('fieldSelectDataToAnalyze');

    //zmienne związane z selektorami
    var selectsChannel = document.getElementById('selectDataToAnalyzeSelectChannelSelector');
    var selectsServer = document.getElementById('selectDataToAnalyzeSelectServerSelector');
    var selectsProgram = document.getElementById('selectDataToAnalyzeSelectProgramSelector');

    //zmienne związane z wyświetlaniem sumy połączeń
    var labelAllConnections = document.getElementById('allConnections');
    var labelUniqueConnections = document.getElementById('uniqueID');

    //Funcja monitorująca zmiany na stronie
    $(document).ready(function() {

        //funckje uruchamiające podczas ładowania strony
        preparingStatistics();
        startHtml();

        //Monitoruje czy programu został zmieniony
        var $setServer = $('#selectDataToAnalyzeSelectProgramSelector');
        $setServer.on('change', function() {
            channelSelectsUpdate();
        });

        //Monitoruje czy kanał został ustawiony lub zmieniony
        var $setChannel = $('#selectDataToAnalyzeSelectChannel, #selectDataToAnalyzeSelectChannelSelector');
        $setChannel.on('change', function() {
            serverSelectsUpdate();
        });

        //Monitorujące zmienę wartości wszystkich dostepnych opcji po za programem i kanału
        var $set = $('#fieldTimeSpan, #fieldTypeOfReport, #selectDataToAnalyzeSelectServer, #selectDataToAnalyzeSelectServerSelector, #selectDataToAnalyzeTheWholeStreamingGroup')
        $set.on('change', function() {
            switchGenerateUrlToIFrame();
        });
    });

    //Funcja wywoływujący funcje generująca url do grafana, przekazując zakres daty wykresu
    function switchGenerateUrlToIFrame(){
                //Najnowsza data logów
            var date = new Date('2022-11-30');

            //Data najnowszych logów, użyte w przypadku zostosowaniu dziennej aktualizacji danych
            /*var date = new Date();
            var day = date.getDate() -1 ;
            var month = date.getMonth() +1;
            var year = date.getFullYear();
            date = year + "-" + month + "-" + day;*/

            //Switch wywoływujący funcje generująca url do grafana, przekazując zakres daty wykresu
            switch(radioButtonTimeSpan.querySelector('input[name="timeSpan"]:checked').id){

                case "timeSpanLastWeek":
                if (document.getElementById("timeSpanChoose").checked != true)
                    generateUrlToIframe(7, date);

                break;

                case "timeSpanLastMonth":
                if (document.getElementById("timeSpanChoose").checked != true)
                    generateUrlToIframe(30, date);
                break;

                case "timeSpanChoose":

                var sqlDateFrom = document.getElementById("chooseDateFrom").value;
                var sqlDateTo = document.getElementById("chooseDateTo").value;

                var dateFrom = new Date(sqlDateFrom);
                var dateTo = new Date(sqlDateTo);

                var differenceInDays = (dateTo.getTime() - dateFrom.getTime()) / (1000 * 3600 * 24);
                if(differenceInDays>0)
                    generateUrlToIframe(differenceInDays, sqlDateTo);
                else if(differenceInDays <= 0)
                    alert("Wrong Dates");
                break;
            }
    }

    //funkcja generująca adres url do iframe oraz liczbę połączeń unikalnych i nieunikalnych do label
    function generateUrlToIframe(days, date) {

        var sqlQueryCount = "select sum(counted_statistics) from prepared_statistics ";
        var sqlQueryCountDistinct = "select sum(counted_statistics_unique) from prepared_statistics ";

        var sqlWhere= "";
        var sqlWhereIFrame = "";

        var toData = new Date(date);
        var fromData = new Date(date);
        fromData.setDate(fromData.getDate() - days);

        //Zmienne z datą w formacie 'YY-MM-DD'
        var toDataSql = toData.getUTCFullYear() + "-" + (toData.getUTCMonth() + 1) + "-" + toData.getUTCDate();
        var fromDataSql = fromData.getUTCFullYear() + "-" + (fromData.getUTCMonth() + 1) + "-" + fromData.getUTCDate();

        toData = Math.floor(toData.getTime());
        fromData = Math.floor(fromData.getTime());
        switch(fieldSelectDataToAnalyze.querySelector('input[name="selectDataToAnalyze"]:checked').id){

        //Wywoływana, kiedy jest zaznaczony Channel
        case "selectDataToAnalyzeSelectChannel":

        var selectProgram = selectsProgram.options[selectsProgram.selectedIndex].text;
        var selectChannel = selectsChannel.options[selectsChannel.selectedIndex].text;

        sqlWhere= " and sgroup_name like '" + selectProgram + "' and stream_name like '" + selectChannel + "' ";
        sqlWhereIFrame = " sgroup_name  like '" + selectProgram + "' and stream_name like '" + selectChannel + "' ";

        rpc.query({
            model: "grafana.snapshots",
            method: "get_snapshot_iframe",
            args: [fromDataSql, toDataSql, radioButtonTypeOfReport.querySelector('input[name="typeOfReport"]:checked').value, sqlWhereIFrame],
                }).then(function (snapshotKey) {

                    //Generowanie url do iframe
                    var snapshotUrl= "http://localhost:3000/dashboard-solo/snapshot/"+ snapshotKey
                        + "?orgId=1&refresh=5s&from="+fromData+"&to="+toData+"&theme=light&panelId=2";

                    chart.src = snapshotUrl;
                });

        break;

        //Wywoływana, kiedy jest zaznaczony Serwer
        case "selectDataToAnalyzeSelectServer":

        var selectProgram = selectsProgram.options[selectsProgram.selectedIndex].text;
        var selectChannel = selectsChannel.options[selectsChannel.selectedIndex].text;
        var selectServer = selectsServer.options[selectsServer.selectedIndex].text;

        sqlWhere= " and sgroup_name like '" + selectProgram + "' and stream_name like '" + selectChannel + "' and server_name like '" + selectServer + "' ";
        sqlWhereIFrame = " sgroup_name  like '" + selectProgram + "' and stream_name like '" + selectChannel + "' and server_name like '" + selectServer + "' ";


        rpc.query({
            model: "grafana.snapshots",
            method: "get_snapshot_iframe",
            args: [fromDataSql, toDataSql, radioButtonTypeOfReport.querySelector('input[name="typeOfReport"]:checked').value, sqlWhereIFrame],
                }).then(function (snapshotKey) {

                    //Generowanie url do iframe
                    var snapshotUrl= "http://localhost:3000/dashboard-solo/snapshot/"+ snapshotKey
                        + "?orgId=1&refresh=5s&from="+fromData+"&to="+toData+"&theme=light&panelId=2";

                    chart.src = snapshotUrl;
                });

        break;

                //Wywoływana, kiedy jest zaznaczony The whole streaming group
        case "selectDataToAnalyzeTheWholeStreamingGroup":

        var selectProgram = selectsProgram.options[selectsProgram.selectedIndex].text;

        sqlWhere = "and sgroup_name  like '" + selectProgram + "' ";;
        sqlWhereIFrame = " sgroup_name  like '" + selectProgram + "' ";

        //wywoływanie funkcji z poziomu python generująca klucz snapshot do Grafana
        rpc.query({
            model: "grafana.snapshots",
            method: "get_snapshot_iframe",
            args: [fromDataSql, toDataSql, radioButtonTypeOfReport.querySelector('input[name="typeOfReport"]:checked').value, sqlWhereIFrame],
                }).then(function (snapshotKey) {

                    //Generowanie url do iframe
                    var snapshotUrl= "http://localhost:3000/dashboard-solo/snapshot/"+ snapshotKey
                        + "?orgId=1&refresh=5s&from="+fromData+"&to="+toData+"&theme=light&panelId=2";

                    chart.src = snapshotUrl;
                });
        break;
        }

        //Generowana jest liczba wszystkich połączeń z wyświetlanego wykresu
        sqlQueryCount += "where start_date BETWEEN \'" + fromDataSql + "\' and \'" + toDataSql + "\'" + sqlWhere + ";";
        generateAllCount(sqlQueryCount);

        //Generowana jest liczba unikalnych połączeń z wyświetlanego wykresu
        sqlQueryCountDistinct += "where start_date BETWEEN \'" + fromDataSql + "\' and \'" + toDataSql + "\'" + sqlWhere + ";";
        generateDistinctCount(sqlQueryCountDistinct);
    }

    //Funcja generująca ilość połączeń z danego okresu czasu do label
    function generateAllCount(sqlQuery){
    rpc.query({
        model: "grafana.snapshots",
        method: "get_sql_query",
        args: [sqlQuery],
            }).then(function (count) {
                labelAllConnections.innerHTML = "All Connections: " + count[0][0];
        });
    }

    //Funcja generująca ilość unikalnych połączeń z danego okresu czasu do label
    function generateDistinctCount(sqlQuery){
    rpc.query({
        model: "grafana.snapshots",
        method: "get_sql_query",
        args: [sqlQuery],
            }).then(function (count) {
                labelUniqueConnections.innerHTML = "Unique Connections: "+ count[0][0];
        });
    }

    //Funcja uruchomiana podczas ładowania strony
    function startHtml(){

        var date = new Date('2022-11-30');

        //Data najnowszych logów, użyte w przypadku zostosowaniu dziennej aktualizacji danych
        /*var date = new Date();
        var day = date.getDate() -1 ;
        var month = date.getMonth() +1;
        var year = date.getFullYear();
        date = year + "-" + month + "-" + day;*/

        var sqlSelect = "select sgroup_name from prepared_statistics group by sgroup_name";

        rpc.query({
            model: "grafana.snapshots",
            method: "get_sql_query",
            args: [sqlSelect],
                }).then(function (listOfPrograms) {
                    var myProgramSelect = "";
                    for (let i=0; i < listOfPrograms.length; i++){
                        myProgramSelect += "<option value=" + i + ">" + listOfPrograms[i] + "</option>";
                        }
                    try{
                        selectsProgram.innerHTML = myProgramSelect;
                        document.getElementById("timeSpanLastWeek").checked = true;
                        document.getElementById("typeOfReportDaily").checked = true;
                        document.getElementById("selectDataToAnalyzeSelectChannel").checked = true;
                        channelSelectsUpdate();

                    }
                    catch{}
            });

        }

    //Funcja przygotowująca Select serwer oraz kanał na stronie internetowej na podstawie wybranego serwera
    function channelSelectsUpdate(){

            //Aktualizowanie Select związane z wyborem Radio Program podczas ładowania strony oraz zmiany serwery
            var sqlSelect = "select stream_name from prepared_statistics where sgroup_name like '";
            sqlSelect += selectsProgram.options[selectsProgram.selectedIndex].text;
            sqlSelect += "' group by stream_name";

            rpc.query({
            model: "grafana.snapshots",
            method: "get_sql_query",

            args: [sqlSelect],
                }).then(function (listOfChannels) {
                    var myChannelSelect = "";
                    for (let i=0; i < listOfChannels.length; i++){
                        myChannelSelect += "<option value=" + i + ">" + listOfChannels[i] + "</option>";
                        }
                    try{
                        selectsChannel.innerHTML = myChannelSelect;
                        serverSelectsUpdate();
                    }
                    catch{}
            });
        }

    function serverSelectsUpdate(){
         //Aktualizowanie Select związane z wyborem channel podczas ładowania strony oraz zmiany serwery

        var sqlSelect = "select server_name from prepared_statistics where sgroup_name like '";
        sqlSelect += selectsProgram.options[selectsProgram.selectedIndex].text;
        sqlSelect += "' and stream_name like '";
        sqlSelect += selectsChannel.options[selectsChannel.selectedIndex].text;
        sqlSelect += "' group by server_name";

        rpc.query({
            model: "grafana.snapshots",
            method: "get_sql_query",
            args: [sqlSelect],
                }).then(function (listOfServers) {
                    var myServerSelect = "";
                    for (let i=0; i < listOfServers.length; i++){
                        myServerSelect += "<option value=" + i + ">" + listOfServers[i] + "</option>";
                        }
                    try{
                        selectsServer.innerHTML = myServerSelect;
                        switchGenerateUrlToIFrame();
                    }
                    catch{}
            });
        }

    //Funkcja przygotowująca logi do Grafana
    function preparingStatistics(){

    //Wywoływana jest funkcja w poziomie Python, sprawdzająca czy danego dnia już były aktualizowane do bazy danych
    rpc.query({
        model: "grafana.snapshots",
        method: "checking_last_update_log_for_grafana",
        args: [],
            }).then(function (notCurrentStatistics) {

                if(notCurrentStatistics == "true"){
                    //Wywołowanie funkcji w poziomie Python, która aktualizuje dane do Grafana
                    rpc.query({
                    model: "grafana.snapshots",
                    method: "preparing_logs_for_grafana",

                    args: [],
                    }).then(function () {
                        });
                }
        });
    }
