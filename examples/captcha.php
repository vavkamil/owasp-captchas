<?php
// Define your username and password
$username = 'admin';
$password = 'pass';
$captcha_secret_key = 'RECAPTCHA-SECRET-KEY';

if($_SERVER['REQUEST_METHOD'] == 'POST') {

    if (empty($_POST['g-recaptcha-response'])) {
        echo 'Please solve the captcha.';
    } else {
        $captcha_response = $_POST['g-recaptcha-response'];

        // To verify the captcha response with Google server, use the following curl request.
        $verify_url = 'https://www.google.com/recaptcha/api/siteverify';
        $ch = curl_init($verify_url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, 'secret=' . $captcha_secret_key . '&response=' . $captcha_response);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $response = curl_exec($ch);
        curl_close($ch);
        $response_data = json_decode($response);

        if ($response_data->success == false) {
            echo 'Invalid captcha.';
        } else if ($_POST['username'] != $username || $_POST['password'] != $password) {
            echo 'Invalid username or password.';
        } else {
            echo 'Login successful.';
        }
    }
} else {
?>

<form method="POST" action="">
  Username: <input type="text" name="username" autocomplete="off"><br>
  Password: <input type="password" name="password"><br>
  <div class="g-recaptcha" data-sitekey="6Lf3s6smAAAAAJhW3or_xM30ZriJpD2zAHAKr2JY"></div><br>
  <input type="submit" value="Submit">
</form>
<script src="https://www.google.com/recaptcha/api.js" async defer></script>

<?php
}
?>
