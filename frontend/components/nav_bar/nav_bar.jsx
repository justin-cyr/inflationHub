import React from 'react';
import { Link } from 'react-router-dom';

import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';

import '../../styles/style_sheet.css';

export default () => {

    const display = (
        <Container fluid>
            <Row>
                <Col><h1>Inflation-Hub</h1></Col>
                <Col className="nav-link">
                    <Link to="/data_viewer">Data Viewer</Link>
                </Col>
                <Col className="nav-link">
                    <Link to="/tips_data">TIPS Data</Link>
                </Col>
                <Col className="nav-link">
                    <Link to="/market_data">Market Data</Link>
                </Col>
                <Col className="nav-link">
                    <Link to="/curve_builder">Curve Builder</Link>
                </Col>
                {/*<Col className="nav-link">
                    <Link to="/knowledge_center">Knowledge Center</Link>
                </Col>*/}
            </Row>
        </Container>
    );

    return (
        <header className="nav_bar">
            {display}
        </header>
    );

};
