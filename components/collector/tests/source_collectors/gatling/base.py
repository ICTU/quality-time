"""Base classes for Gatling collectors."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class GatlingTestCase(SourceCollectorTestCase):
    """Base class for Gatling collector unit tests."""

    SOURCE_TYPE = "gatling"
    TRANSACTION1 = "Transaction 1"
    TRANSACTION2 = "Transaction 2"
    GATLING_STATS_HTML = """
<table id="container_statistics_body" class="statistics-in extensible-geant">
    <tbody>
        <tr data-parent="ROOT">
            <td class="total col-1">
                <div class="expandable-container">
                    <span id="req_t1-2031010915" style="margin-left: 0px;" class="expand-button hidden">&nbsp;</span>
                    <a href="req_t1-2031010915.html" class="withTooltip">
                        <span class="table-cell-tooltip" id="parent-stats-table-req_t1-2031010915"
                        data-toggle="popover" data-placement="right" data-container="body" data-content="">
                            <span onmouseover="isEllipsed('stats-table-req_t1-2031010915')"
                            id="stats-table-req_t1-2031010915" class="ellipsed-name">Transaction 1</span>
                        </span>
                    </a>
                    <span class="value" style="display:none;">0</span>
                </div>
            </td>
            <td class="value total col-2">1</td>
            <td class="value ok col-3">1</td>
            <td class="value ko col-4">-</td>
            <td class="value ko col-5">0</td>
            <td class="value total col-6">0</td>
            <td class="value total col-7">317</td>
            <td class="value total col-8">317</td>
            <td class="value total col-9">317</td>
            <td class="value total col-10">317</td>
            <td class="value total col-11">317</td>
            <td class="value total col-12">317</td>
            <td class="value total col-13">317</td>
            <td class="value total col-14">0</td>
        </tr>
        <tr data-parent="ROOT">
            <td class="total col-1">
                <div class="expandable-container">
                    <span id="req_t2-1955276709" style="margin-left: 0px;" class="expand-button hidden">&nbsp;</span>
                    <a href="req_t2-1955276709.html" class="withTooltip">
                        <span class="table-cell-tooltip" id="parent-stats-table-req_t2-1955276709"
                        data-toggle="popover" data-placement="right" data-container="body" data-content="">
                            <span onmouseover="isEllipsed('stats-table-req_t2-1955276709')"
                            id="stats-table-req_t2-1955276709" class="ellipsed-name">Transaction 2</span>
                        </span>
                    </a>
                    <span class="value" style="display:none;">0</span>
                </div>
            </td>
            <td class="value total col-2">2520</td>
            <td class="value ok col-3">2516</td>
            <td class="value ko col-4">4</td>
            <td class="value ko col-5">0.16</td>
            <td class="value total col-6">9.88</td>
            <td class="value total col-7">6</td>
            <td class="value total col-8">8</td>
            <td class="value total col-9">9</td>
            <td class="value total col-10">13</td>
            <td class="value total col-11">24</td>
            <td class="value total col-12">756</td>
            <td class="value total col-13">10</td>
            <td class="value total col-14">22</td>
        </tr>
    </tbody>
</table>
"""
