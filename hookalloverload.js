function getGenericInterceptor(className, func, parameters) {
    var args = [];
    var valArgs = [];
    var i = 0;
    for (i = 0; i < parameters.length; i++) {
        args.push('arg_' + i);
        valArgs.push("'<<" + parameters[i] + ">><<'+ arg_" + i + "+'>>'");
    }
    // var script = "result =
    // this.__FUNCNAME__(__SEPARATED_ARG_NAMES__);log='[*]Stack trace:\\n';thread =
    // Java.use('java.lang.Thread').currentThread().getStackTrace();for (var i =
    // thread.length-3; i >=2; i--)
    // {log+=thread[i].getClassName()+'.'+thread[i].getMethodName()+'->';}var
    // olog=Java.use('android.util.Log');olog.d('[JOSEBEO]',log);\nreturn result;"
    // var script = "result = this.__FUNCNAME__(__SEPARATED_ARG_NAMES__);log='';thread = Java.use('" +
    //         "java.lang.Thread').currentThread().getStackTrace();for (var i = thread.length-" +
    //         "3; i>=3; i--) {log+=thread[i].getClassName()+'.'+thread[i].getMethodName()+'->" +
    //         "';}logmessage = '__CLASSNAME__.__FUNCNAME__->'+__SEPARATED_ARG_VALUE__;logmess" +
    //         "age+='->'+result;log+=logmessage;send(log);\nreturn result;"
    // var _time = new Date().getTime();
    // send(Date().now());
    var script = "var b = Java.use('java.util.Date');var a = b.$new();var _time = a.getTime();result = this.__FUNCNAME__(__SEPARATED_ARG_NAMES__);logmessage ='['+_time+']'+ '[__CLASSNAME__] [__FUNCNAME__]'+__SEPARATED_ARG_VALUE__;logmessage+='[Return] ['+result+']';send(logmessage);\nreturn result;";

    script = script.replace(/__FUNCNAME__/g, func);
    script = script.replace(/__SEPARATED_ARG_NAMES__/g, args.join(', '));
    script = script.replace(/__SEPARATED_ARG_VALUE__/g, valArgs.join('+ '));
    script = script.replace(/__CLASSNAME__/g, className);
    script = script.replace(/\+  \+/g, '+');
    script = script.replace(/\+;/g, ';');
    args.push(script);
    // console.log(script);
    const cb = Function.apply(null, args);
    return cb

}

function hookall(className, func, cb) {
    const clazz = Java.use(className);
    // console.log(clazz[func].overloads);
    var aaa = clazz[func].overloads;
    
    //frida-12.4.4
    var i = 0;
    for (i in aaa) {
        if (aaa[i].hasOwnProperty('argumentTypes')) {
            var parameters = [];
            var j = 0;
            for (j in aaa[i].argumentTypes) {
                parameters.push(aaa[i].argumentTypes[j].className); 
            }
            const cb = getGenericInterceptor(className, func, parameters);
            clazz[func].overload.apply('this', parameters).implementation = cb;
        }
    }
}

if (Java.available) {
    console.log("Start loading script!");
    // Switch to the Java context
    Java.perform(function () {

        try {
            hookall("android.telephony.TelephonyManager", "getDeviceId", "a");
        } catch (err) {
            send("[-]Error in: android.telephony.TelephonyManager.getDeviceId");
        }

        try {
            hookall("android.telephony.TelephonyManager", "getLine1Number", "a");
        } catch (err) {
            send("[-]Error in: android.telephony.TelephonyManager.getLine1Number");
        }

        try {
            hookall("android.telephony.TelephonyManager", "getSubscriberId", "a");
        } catch (err) {
            send("[-]Error in: android.telephony.TelephonyManager.getSubscriberId");
        }

        try {
            hookall("android.telephony.TelephonyManager", "getImei", "a");
        } catch (err) {
            send("[-]Error in: android.telephony.TelephonyManager.getImei");
        }

        try {
            hookall("android.telephony.TelephonyManager", "getMeid", "a");
        } catch (err) {
            send("[-]Error in: android.telephony.TelephonyManager.getMeid");
        }
        try {
            hookall("android.telephony.SmsManager", "sendTextMessage", "a");
        } catch (err) {
            send("[-]Error in: android.telephony.SmsManager.sendTextMessage");
        }

        try {
            hookall("android.telephony.SmsManager", "sendMultipartTextMessage", "a");
        } catch (err) {
            send("[-]Error in: android.telephony.SmsManager.sendMultipartTextMessage");
        }

        try {
            hookall("android.telephony.SmsManager", "getSubscriptionId", "a");
        } catch (err) {
            send("[-]Error in: android.telephony.SmsManager.getSubscriptionId");
        }

        try {
            hookall(
                "android.telephony.SmsManager","sendTextMessageWithoutPersisting","a"
            );
        } catch (err) {
            send(
                "[-]Error in: android.telephony.SmsManager.sendTextMessageWithoutPersisting"
            );
        }


        console.log("[*]End loading script!");
    })
}
