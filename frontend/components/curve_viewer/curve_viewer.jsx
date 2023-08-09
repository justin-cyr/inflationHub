import React from 'react';
import $ from 'jquery';

import Alert from 'react-bootstrap/Alert';
import Button from 'react-bootstrap/Button';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Modal from 'react-bootstrap/Modal';
import Row from 'react-bootstrap/Row';

class CurveViewer extends React.Component {

    constructor(props) {
        super(props);

        this._isMounted = false;
        this.state = {
            curve_templates: []
        }
    }

    getCurveTemplates() {
        $.ajax({
            url: '/get_curve_templates',
            method: 'GET',
            success: (response) => {
                this._isMounted && this.setState({
                    curve_templates: response.curve_templates
                })
            }
        });
    }

    componentDidMount() {
        this._isMounted = true;
        this.getCurveTemplates();
    }

    componentWillUnmount() {
        this._isMounted = false;
    }

    render() {

        return (
            <Container fluid>
                <Row>
                    Curve viewer
                </Row>
            </Container>
        );
    }

}

export default CurveViewer;
