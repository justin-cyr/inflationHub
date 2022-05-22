import React from 'react';
import $ from 'jquery';

import CloseButton from 'react-bootstrap/CloseButton';
import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';

class CurveBuilder extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            curveDataPoints: [],
            // selection choices
            supportedCurveDataPointTypes: []
        }

        // bind methods

    }

    componentDidMount() {
        // Request selection list choices
        $.ajax({
            url: '/supported_curve_data_point_types',
            method: 'GET',
            success: (response) => {
                this.setState({
                    supportedCurveDataPointTypes: response.choices
                })
            }
        });
    }

    render() {

        return (
            <Container fluid>
                {'content'}
            </Container>
        );
    }

}

export default CurveBuilder;
