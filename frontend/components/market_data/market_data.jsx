import React from 'react';

import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import ListGroup from 'react-bootstrap/ListGroup';
import Row from 'react-bootstrap/Row';
import Tab from 'react-bootstrap/Tab';

import TreasuriesMonitor from './treasuries_monitor_container';
import BondFuturesMonitor from './bond_futures_monitor_container';

const upColor = '#198754';  // green
const downColor = '#dc3545';  // red
const unchColor = '#bdbdbd'; // default text color

class MarketData extends React.Component {

    constructor(props) {
        super(props);

        this.getChangeColor = this.getChangeColor.bind(this);
    }
    
    getChangeColor(quoteObj, key, field) {
        if ((key in quoteObj) && (field in quoteObj[key])) {
            if (quoteObj[key][field] > 0) {
                return upColor;
            }
            else if (quoteObj[key][field] < 0) {
                return downColor;
            }
        }
        return unchColor;
    }

    render() {

        return (
            <Container fluid>
                <Row>
                    <Tab.Container id="market-data-tabs" defaultActiveKey="#/market_data/treasuries_monitor">
                        <Row>
                            <Col
                                md="auto"
                            >
                                <ListGroup>
                                    <ListGroup.Item action href="#/market_data/treasuries_monitor">Treasuries Monitor</ListGroup.Item>
                                    <ListGroup.Item action href="#/market_data/bond_futures_monitor">Bond Futures Monitor</ListGroup.Item>
                                </ListGroup>
                            </Col>
                            <Col
                                style={{ textAlign: "center" }}
                            >
                                <Tab.Content>

                                    <Tab.Pane eventKey="#/market_data/treasuries_monitor">
                                        <h3>{'Treasuries Monitor'}</h3>
                                        <TreasuriesMonitor getChangeColor={this.getChangeColor} />
                                    </Tab.Pane>

                                    <Tab.Pane eventKey="#/market_data/bond_futures_monitor">
                                        <h3>{'Bond Futures Monitor'}</h3>
                                        <BondFuturesMonitor getChangeColor={this.getChangeColor} />
                                    </Tab.Pane>

                                </Tab.Content>
                            </Col>
                        </Row>
                    </Tab.Container>
                </Row>
            </Container>
        );
    }
  }

export default MarketData;